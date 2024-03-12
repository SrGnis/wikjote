from __future__ import annotations
from typing import Any

import re

import logging
from wikjote.pipeline.handler import Handler


class StructurizeHandler(Handler):
    _input_type = [list[dict]]
    _output_type = list[dict]
    _concurrent = True
    logger: logging.Logger = logging.getLogger("wikjote")

    def process(self, data: list[dict]) -> list[dict]:

        result = []
        for page in data:
            try:
                word = page["page"]
                for languaje in page["sections"]:
                    if languaje["type"] != "languaje":
                        self.logger.warning(
                            "Expected languaje section but %s section found in word %s",
                            languaje["type"],
                            word,
                        )
                        continue
                    word_obj = {}
                    word_obj["word"] = word
                    word_obj["languaje"] = languaje["name"]

                    self.process_sub_sections(languaje, word_obj)

                    result.append(word_obj)
            except Exception:
                self.logger.error(
                    "Can not structurize page %s",
                    page["page"],
                    exc_info=1,  # type: ignore : this is what the docs says
                )

        return result

    def process_sub_sections(self, section: dict[str, Any], word_obj: dict):
        for sub_section in section["sub_sections"]:
            match sub_section["type"]:
                case "etymology":
                    self.process_etymology(sub_section, word_obj)
                case section_type if section_type in ["senses", "verb_form"]:
                    self.process_senses(sub_section, word_obj)
                case "idioms":
                    pass
                case "additional_info":
                    pass
                case "translations":
                    pass
                case "flexive_form":
                    self.process_sub_sections(sub_section, word_obj)
                case "see_more":
                    pass
                case _:
                    if "Etimología" in sub_section["name"]:
                        self.process_etymology(sub_section, word_obj)
                    else:
                        self.logger.warning(
                            "Sub section of type %s and name %s not processed for word %s",
                            sub_section["type"],
                            sub_section["name"],
                            word_obj["word"],
                        )

    def process_etymology(self, section: dict[str, Any], word_obj: dict[str, Any]):
        if word_obj.get("etymologies") is None:
            word_obj["etymologies"] = []
        word_obj["etymologies"].append(section["contents"])
        self.process_sub_sections(section, word_obj)

    def process_senses(self, section: dict[str, Any], word_obj: dict[str, Any]):
        current_pos = self.get_pos(section, word_obj)

        etymologies: list | None = word_obj.get("etymologies")
        if etymologies is None:
            last_etymology = None
        else:
            last_etymology = len(etymologies)

        contents = section.get("contents")
        if contents is None:
            contents = {}

        meanings: "list[dict]" = contents.get("senses", [])
        for meaning in meanings:

            synonyms = self.clear_attribute(meaning["attributes"].get("sinónimos"))

            hiponyms = meaning["attributes"].get("hipónimos")
            if isinstance(hiponyms, str):
                hiponyms = hiponyms.split(", ")

            uses = meaning["attributes"].get("usos")
            if isinstance(uses, str):
                uses = uses.split(", ")

            scopes = meaning["attributes"].get("ámbitos")
            if isinstance(scopes, str):
                scopes = scopes.split(", ")

            meanings = current_pos.get("meanings", [])
            current_pos["meanings"] = meanings

            meanings.append(
                {
                    "etimology": last_etymology,
                    "meaning": meaning["content"],
                    "synonyms": synonyms,
                    "hiponyms": hiponyms,
                    "scopes": scopes,
                    "uses": uses,
                }
            )

        current_pos["inflection"] = contents.get("inflection", None)

        self.process_sub_sections(section, word_obj)

    def get_pos(self, section: dict[str, Any], word_obj: dict[str, Any]):
        parts_of_speech = word_obj.get("pos")
        if parts_of_speech is None:
            parts_of_speech = {}
            word_obj["pos"] = parts_of_speech

        raw_pos: str = section["name"]

        pos = self.translate_pos(raw_pos.split(" "))

        current_pos: dict = parts_of_speech  # type: ignore
        for pos_entry in pos:
            tmp = current_pos.get(pos_entry)  # type: ignore
            if tmp is None:
                current_pos[pos_entry] = {}
            current_pos = current_pos.get(pos_entry)  # type: ignore

        return current_pos

    @staticmethod
    def clear_attribute(attribute: Any) -> Any:
        if isinstance(attribute, str):
            matches = re.finditer(r"\(.*?\)", attribute)
            for match in matches:
                attribute = (
                    attribute[0 : match.start()]
                    + attribute[match.start() : match.end()].replace(" ", " ")
                    + attribute[match.end() :]
                )
            attribute = attribute.split(", ")

        return attribute

    @classmethod
    def translate_pos(cls, pos_list: list[str]) -> list[str]:

        new_pos_list = []
        for pos_entry in pos_list:
            pos_entry = pos_entry.lower()
            translation = cls.pos_translations.get(pos_entry, None)
            if translation is None:
                cls.logger.warning("POS %s without translation", pos_entry)
                translation = pos_entry

            new_pos_list.append(translation)

        return new_pos_list

    pos_translations: dict[str, str] = {
        "sustantivo": "noun",
        "adjetivo": "adjetive",
        "determinante": "determiner",
        "verbo": "verb",
        "adverbio": "adverb",
        "pronombre": "pronoun",
        "masculino": "masculine",
        "femenino": "femenine",
        "indefinido": "indefinite",
        "cardinal": "cardinal",
        "ordinal": "ordinal",
        "preposición": "preposition",
        "transitivo": "transitive",
        "intransitivo": "intransitive",
        "posesivo": "possessive",
        "de cantidad": "quantity",
        "forma verbal": "verb_form",
        "interjección": "interjection",
    }
