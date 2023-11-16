from copy import deepcopy

from lxml.etree import ElementBase

from queries import xpathqueries


def parse_table(root: ElementBase):
    row_skips = [8, 9, 15, 21, 22, 26, 32, 35]  # rows that should not be processed
    sublevels = {
        8: {"name": "indicativo", "end": 21, "clear": False},
        21: {"name": "subjuntivo", "end": 32, "clear": False},
        32: {"name": "imperativo"},
    }
    rm_sublevel = {}  # auxiliar dict to help remove sublevels when a row is reached
    flection_obj = None
    flection_table_found: list[ElementBase] = root.xpath(xpathqueries["flection"])
    if len(flection_table_found) > 0:
        flection_table: ElementBase = flection_table_found[0]
        rows: list[ElementBase] = flection_table.xpath(".//tr")

        flection_obj = {}
        target_level = []
        top_headers = []

        normalize_rows(rows, row_skips, sublevels)

        for row_index, row in enumerate(rows):
            # Remove sub level
            if rm_sublevel.get(row_index, None) is not None:
                sublevel = rm_sublevel[row_index]
                target_level = target_level[: target_level.index(sublevel["name"])]
                target = get_dict_level(flection_obj, target_level)
                clear = sublevel.get("clear", False)
                if clear:
                    top_headers = []

            # Add sub level
            if sublevels.get(row_index, None) is not None:
                sublevel = sublevels[row_index]
                target = get_dict_level(flection_obj, target_level)
                target[sublevel["name"]] = {}
                target_level.append(sublevel["name"])
                end = sublevel.get("end", None)
                if end is not None:
                    rm_sublevel[end] = sublevel

            if row_index in row_skips:
                continue

            row_children = row.getchildren()
            row_has_th = False

            # iterate over the children of each row using num_cols to take care of the cells with rowspan
            for col_index in range(len(row_children)):
                target = get_dict_level(flection_obj, target_level)
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
                    if dict_content is None:
                        target[header] = [get_all_text(element)]
                    else:
                        content = get_all_text(element)
                        if content not in dict_content:
                            target[header].append(content)
    return flection_obj


# TODO: rowspan CAUTION colspan should be normalized before normalizing rowspans
def normalize_rows(rows: list[ElementBase], row_skips: list[int], sublevels: dict):
    last_sublevel = None
    num_cols = len(rows[0].xpath("./*[self::th | self::td]")) + sum(
        int(e.get("colspan", "1")) - 1 for e in rows[0].xpath("./*[@colspan]")
    )
    for row_index, row in enumerate(rows):
        with_colspan: list[ElementBase] = row.xpath("./*[@colspan]")
        for element in with_colspan:
            colspan = int(element.get("colspan", "1"))
            element.attrib.pop("colspan")
            if len(with_colspan) < num_cols and colspan == num_cols:
                if row_index not in row_skips:
                    row_skips.append(row_index)
                    # TODO: add sublevels
                    sublevels[row_index] = {
                        "name": get_all_text(row).strip(),
                        "clear": True,
                    }
                    if last_sublevel is not None:
                        sublevels[last_sublevel]["end"] = row_index
                    last_sublevel = row_index
                break
            for i in range(colspan - 1):
                element.addnext(deepcopy(element))
    for row_index, row in enumerate(rows):
        elements: list[ElementBase] = row.xpath("./*[self::th | self::td]")
        for col_index, element in enumerate(elements):
            if element.get("rowspan", None) is not None:
                rowspan = int(element.get("rowspan", None))
                element.attrib.pop("rowspan")
                for offset in range(rowspan - 1):
                    rows[row_index + offset + 1].insert(col_index, deepcopy(element))
    return num_cols


def get_dict_level(dict_obj, levels):
    target = dict_obj
    try:
        for level in levels:
            target = target[level]
    except Exception:
        target = dict_obj
    return target


def get_all_text(element: ElementBase) -> str:
    return "".join(element.itertext())  # type: ignore
