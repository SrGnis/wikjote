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

        # main
        result = []

        for page in data:
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

        return result

    def process_sub_sections(self, section: dict[str, Any], word_obj: dict):
        for sub_section in section["sub_sections"]:
            match sub_section["type"]:
                case "etymology":
                    self.process_etymology(sub_section, word_obj)
                case "senses":
                    self.process_senses(sub_section, word_obj)
                case "idioms":
                    pass
                case "additional_info":
                    pass
                case "translations":
                    pass
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
        parts_of_speech = word_obj.get("pos")
        if parts_of_speech is None:
            parts_of_speech = {}
            word_obj["pos"] = parts_of_speech

        # TODO Sustantivo masculino is not a pos only Sustantivo is a pos
        current_pos = parts_of_speech.get(section["name"])
        if current_pos is None:
            current_pos = {
                "pos": section["name"],  # a bit of redundancy
                "meanings": [],
            }
            parts_of_speech[section["name"]] = current_pos

        etymologies: list | None = word_obj.get("etymologies")
        if etymologies is None:
            last_etymology = None
        else:
            last_etymology = len(etymologies)

        contents = section["contents"]
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

            current_pos["meanings"].append(
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
