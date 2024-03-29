import copy
import os
import wikjote.config as config
from exceptions import XMLNotFound
from lxml import etree
from lxml.etree import ElementBase
from queries import xpathqueries
from libzim.reader import Archive
import traceback
import json
import re

from page import Page

non_senses = [
    "Información adicional",
    "Locuciones",
    "Etimología",
    "Véase también",
    "Traducciones",
    "Abreviaciones",
    "Derivados",
    "Pronunciación y escritura",
    "Refranes",
    "Conjugacións",
    "Información avanzada",
    "Ejemplos",
]

cat_procesed = {}


def find_or_fail(html: ElementBase, query: str):
    result = find(html, query)
    if len(result) == 0:
        raise XMLNotFound(query)
    return result


def find(html: ElementBase, query: str):
    result: list[ElementBase] = html.xpath(query)
    return result


def process_zim2():
    print("Processing zim")

    zim = Archive(config.WikjoteConfig.zimfile)

    with open(
        os.path.join(config.WikjoteConfig.downloads_dir, "eswiktionary-titles"),
        encoding="utf8",
    ) as f:
        f = ["flor"]
        for lema in f:
            try:
                lema = lema.strip()
                entry = zim.get_entry_by_path(lema)
                entry_content = bytes(entry.get_item().content).decode("UTF-8")
                entry_html: ElementBase = etree.HTML(entry_content)  # type: ignore

                page = Page(entry_html, lema)

                print("Page:", page.lema, "Languajes:", page.languajes)  # debug

            except Exception as e:
                print("Error in lema: ", lema)


def process_zim():
    print("Processing zim")

    zim = Archive(config.WikjoteConfig.zimfile)

    with open(
        os.path.join(config.WikjoteConfig.downloads_dir, "eswiktionary-titles"),
        encoding="utf8",
    ) as f:
        f = ["ARPU"]
        for lema in f:
            try:
                lema = lema.strip()
                entry = zim.get_entry_by_path(lema)
                page = bytes(entry.get_item().content).decode("UTF-8")

                html: ElementBase = etree.HTML(page)  # type: ignore

                if False:
                    languages = find_or_fail(
                        html, xpathqueries["language_section_chosed"].format("Español")
                    )
                else:
                    languages = find_or_fail(html, xpathqueries["language_sections"])

                entry_obj = {}
                entry_obj["lema"] = lema

                for language in languages:
                    language_obj = {}
                    x = find_or_fail(language, xpathqueries["section_name"])
                    language_name = get_all_text(
                        find_or_fail(language, xpathqueries["section_name"]).pop()
                    )
                    inner_sections = find(language, xpathqueries["inner_sections"])
                    categories_array = []

                    for section in inner_sections:
                        section_name = get_all_text(
                            find_or_fail(section, xpathqueries["section_name"]).pop()
                        )

                        if section_name not in non_senses:
                            section_obj = process_senses_section(
                                section, section_name, language, lema
                            )
                            categories_array.append(copy.deepcopy(section_obj))
                        else:
                            language_obj[section_name] = fire_callback(
                                section_name, section, section_name, language, lema
                            )

                    if len(categories_array) > 0:
                        language_obj["categories"] = categories_array

                    # if(len(conjugation) > 0):
                    #     conjugation = get_flection(conjugation[0], es_section)
                    #     entry_obj['conjugation'] = conjugation

                    entry_obj[language_name] = copy.deepcopy(language_obj)

                result = json.dumps(entry_obj, ensure_ascii=False, indent=2)

                # print(result)

            except Exception as e:
                print("Error in lema: ", lema)
                # traceback.print_exc()

        # print(json.dumps(cat_procesed, ensure_ascii=False, indent=2))


def process_section_to_text(section, section_name, language, lema):
    contents = find(section, "./summary/following-sibling::*")
    res = ""
    for content in contents:
        res += get_all_text(content).strip()
    return res


def process_list(section, section_name, language, lema):
    contents = find(section, ".//li")
    res = []
    for content in contents:
        res.append(get_all_text(content).strip())
    return res


def process_tranlations(section, section_name, language, lema):
    contents = find(section, ".//li")
    res = {}
    for content in contents:
        txt = get_all_text(content).strip()
        txt = re.sub("\[.*\]", "", txt)  # remove [1]
        txt = re.sub("\(.*\).*", "", txt)  # remove (es)...
        txt = txt.split(":")
        if len(txt) == 2:
            res[txt[0].strip()] = txt[1].strip()
    return res


def process_senses_section(section, section_name, language, lema):
    category_obj = {}

    try:
        category_obj["type"] = section_name

        flection = get_flection(section, language)
        category_obj["flection"] = flection

        senses = find(section, xpathqueries["senses"])
        sense_array = []
        for sense in senses:
            # if the sense has ul probably is not a sense
            if len(find(sense, ".//ul")) > 0:
                continue

            sense_obj = {}
            try:
                head = find_or_fail(sense, xpathqueries["sense_title"])
                sense_obj["head"] = "".join(head[0].itertext())  # type: ignore

                content = find_or_fail(sense, xpathqueries["sense_content"])
                sense_obj["content"] = "".join(content[0].itertext())  # type: ignore
            except:
                sense_obj = None
                # check if the sense is malformated
                has_dt = len(find(sense, "./dt")) > 0
                dd = find(sense, "./dd")
                has_dd = len(dd) > 0
                if has_dd and not has_dt:
                    sense_array[-1]["content"] += "\n" + get_all_text(dd[0])

            if sense_obj != None:
                sense_array.append(copy.deepcopy(sense_obj))

        category_obj["senses"] = sense_array

        n = cat_procesed.get(category_obj["type"], 0)
        cat_procesed[category_obj["type"]] = n + 1

    except Exception as e:
        print("Error in category:", section_name[0].text, "of lema:", lema)
    finally:
        return category_obj


def get_flection(category, es_section):
    row_skips = [8, 9, 15, 21, 22, 26, 32, 35]  # rows that should not be processed
    sublevels = {
        8: {"name": "indicativo", "end": 21, "clear": False},
        21: {"name": "subjuntivo", "end": 32, "clear": False},
        32: {
            "name": "imperativo",
        },
    }
    rm_sublevel = {}  # auxiliar dict to help remove sublevels when a row is reached
    flection_obj = None
    flection_table = find(category, xpathqueries["flection"])
    if len(flection_table) > 0:
        rows = find(flection_table[0], ".//tr")  # type: ignore

        flection_obj = {}
        target_level = []
        top_headers = []

        num_cols = normalize_rows(rows, row_skips, sublevels)

        for row_index, row in enumerate(rows):
            # Remove sub level
            if rm_sublevel.get(row_index, None) != None:
                sublevel = rm_sublevel[row_index]
                target_level = target_level[: target_level.index(sublevel["name"])]
                target = get_dict_level(flection_obj, target_level)
                clear = sublevel.get("clear", False)
                if clear:
                    top_headers = []

            # Add sub level
            if sublevels.get(row_index, None) != None:
                sublevel = sublevels[row_index]
                target = get_dict_level(flection_obj, target_level)
                target[sublevel["name"]] = {}
                target_level.append(sublevel["name"])
                end = sublevel.get("end", None)
                if end != None:
                    rm_sublevel[end] = sublevel

            if row_index in row_skips:
                continue

            row_children = row.getchildren()
            row_has_th = False

            # iterate over the children of each row using num_cols to take care of the cells with rowspan
            for col_index in range(len(row_children)):
                target = get_dict_level(flection_obj, target_level)
                if True:
                    element: ElementBase = row_children[col_index]

                    if element.tag == "th":
                        row_has_th = True
                        if col_index <= len(top_headers) - 1:
                            if col_index == 0:
                                top_headers[col_index] = get_all_text(element)
                            else:
                                top_headers[col_index] += "," + get_all_text(element)
                        else:
                            top_headers.insert(col_index, get_all_text(element))
                    if element.tag == "td":
                        if row_has_th:
                            header = ",".join([top_headers[0], top_headers[col_index]])
                        else:
                            header = ",".join([top_headers[col_index]])

                        dict_content = target.get(header, None)
                        if dict_content == None:
                            target[header] = [get_all_text(element)]
                        else:
                            content = get_all_text(element)
                            if content not in dict_content:
                                target[header].append(content)
    return flection_obj


def normalize_rows(rows: list[ElementBase], row_skips: list[int], sublevels: dict):
    last_sublevel = None
    num_cols = len(find(rows[0], "./*[self::th | self::td]")) + sum(
        int(e.get("colspan", "1")) - 1 for e in find(rows[0], "./*[@colspan]")
    )
    for row_index, row in enumerate(rows):
        with_colspan = find(row, "./*[@colspan]")
        for element in with_colspan:
            colspan = int(element.get("colspan", "1"))
            element.attrib.pop("colspan")
            if len(with_colspan) < num_cols and colspan == num_cols:
                if row_index not in row_skips:
                    row_skips.append(row_index)

                    sublevels[row_index] = {
                        "name": get_all_text(row).strip(),
                        "clear": True,
                    }
                    if last_sublevel != None:
                        sublevels[last_sublevel]["end"] = row_index
                    last_sublevel = row_index
                break
            for i in range(colspan - 1):
                element.addnext(copy.deepcopy(element))
    for row_index, row in enumerate(rows):
        elements = find(row, "./*[self::th | self::td]")
        for col_index, element in enumerate(elements):
            if element.get("rowspan", None) != None:
                rowspan = int(element.get("rowspan", None))
                element.attrib.pop("rowspan")
                for offset in range(rowspan - 1):
                    rows[row_index + offset + 1].insert(
                        col_index, copy.deepcopy(element)
                    )
    return num_cols


def get_all_text(element: ElementBase) -> str:
    return "".join(element.itertext())  # type: ignore


def get_dict_level(dict_obj, levels):
    target = dict_obj
    try:
        for level in levels:
            target = target[level]
    except:
        target = dict_obj
    return target


section_callbacks = {
    "Etimología": process_section_to_text,
    "Locuciones": process_list,
    "Información adicional": process_list,
    "Véase también": process_list,
    "Traducciones": process_tranlations,
}


def fire_callback(event, section, section_name, language, lema):
    cllbk = section_callbacks.get(event, None)
    if cllbk == None:
        return None

    return cllbk(section, section_name, language, lema)
