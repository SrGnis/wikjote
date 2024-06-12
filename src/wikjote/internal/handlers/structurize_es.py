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
                case "flexive_form":
                    self.process_sub_sections(sub_section, word_obj)
                case "conjugation":
                    self.process_conjugation(sub_section, word_obj)
                case "idioms":
                    pass # TODO
                case "additional_info":
                    pass # TODO
                case "translations":
                    pass # TODO
                case "see_more":
                    pass # TODO
                case _:
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

    def process_conjugation(self, section: dict[str, Any], word_obj: dict[str, Any]):
        try:
            target = word_obj["pos"][-1] # we suppose that before a conjugation section there is a sense section 
            conjugation = self.inflection_table_to_list(section["contents"])
            conjugation = filter(lambda x: x != "" and "Se emplea" not in x, conjugation)
            conjugation = [x.split(" ")[-1] for x in conjugation]
            conjugation = list(dict.fromkeys(conjugation))
            target['inflection'].extend(conjugation)
        except:
            self.logger.warning('Cannot process the the conjugation of word %s', word_obj["word"]) 
        self.process_sub_sections(section, word_obj)

    def process_senses(self, section: dict[str, Any], word_obj: dict[str, Any]):
        current_pos = self.get_pos(section, word_obj)
        if current_pos is None:
            return

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

        current_pos["inflection"] = self.inflection_table_to_list(contents.get("inflection", None))

        self.process_sub_sections(section, word_obj)

    def inflection_table_to_list(self, table: dict[str, Any] | None ) -> list[str]:
        tmp_res: list[str] = []

        if table is None:
            return []

        for value in table.values():
            if isinstance(value, dict):
                tmp_res.extend(self.inflection_table_to_list(value))
            elif isinstance(value, list):
                tmp_res.extend(value)
            elif isinstance(value, str):
                tmp_res.append(value)

        res: list[str] = []
        for value in tmp_res:
            value = value.replace(',o ', ', ')
            value = value.split(',')
            res.extend(value)

        res = [x.strip() for x in res]
        res = list(dict.fromkeys(res))

        return res

    def get_pos(self, section: dict[str, Any], word_obj: dict[str, Any]) -> dict[str, list[Any]] | None:
        parts_of_speech = word_obj.get("pos")
        if parts_of_speech is None:
            parts_of_speech = []
            word_obj["pos"] = parts_of_speech

        raw_pos: str = section["name"]

        # {"primary": ["noun"], "attr": ["masculine"]}
        pos = self.translate_pos(raw_pos, word_obj.get("word", "_None_"))
        if pos is None:
            return None
        
        parts_of_speech.append(pos)
        
        return pos

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
    def translate_pos(cls, raw_pos: str, word: str) -> dict[str, list[str]] | None:

        # clean it
        raw_pos = raw_pos.lower()
        raw_pos = raw_pos.replace(" ", " ")
        raw_pos = raw_pos.replace(",", "")
        raw_pos = raw_pos.replace(".", "")
        raw_pos = re.sub(r"\[.*\]", "", raw_pos)

        pos_list = raw_pos.split()

        new_pos = {"primary": [], "attr": []}
        for pos_entry in pos_list:
            if pos_entry in cls.pos_rules["ban"]:
                return None
            if pos_entry in cls.pos_rules["ignore"]:
                continue
            primary = cls.pos_rules["primary"].get(pos_entry, None)
            if primary is not None:
                new_pos["primary"].append(primary)
                continue
            attr = cls.pos_rules["attr"].get(pos_entry, None)
            if attr is not None:
                new_pos["attr"].append(attr)
                continue
            cls.logger.warning('POS not found for %s in %s',pos_entry, word)

        return new_pos

    pos_rules = {
        "primary": {
            "artículo": "article",
            "conjunción": "conjunction",
            "contracción": "contraction",
            "acrónimo": "acronym",
            "expresión": "expression",
            "frase": "phrase",
            "letra": "letter",
            "locución": "locution",
            "onomatopeya": "onomatopoeia",
            "participio": "participle", 
            "prefijo": "prefix",
            "refrán": "proverb",
            "sigla": "acronym",
            "sílaba": "syllable",
            "símbolo": "symbol",
            "sufijo": "suffix",
            "sufija": "suffix",
            "sustantivo": "noun",
            "adjetivo": "adjective",
            "determinante": "determiner",
            "verbo": "verb",
            "adverbio": "adverb",
            "pronombre": "pronoun",
            "interjección": "interjection",
            "preposición": "preposition",
            "forma": "form",
        },
        "attr": {
            "masculino": "masculine",
            "femenino": "femenine",
            "indefinido": "indefinite",
            "cardinal": "cardinal",
            "ordinal": "ordinal",
            "transitivo": "transitive",
            "intransitivo": "intransitive",
            "posesivo": "possessive",
            "posesiva": "possessive",
            "cantidad": "quantity",
            "femenina": "feminine",
            "interrogativa": "interrogative",
            "verbal": "verb",
            "sustantiva": "noun",
            "adjetiva": "adjective",
            "adjetival": "adjective",
            "adverbial": "adverb",
            "masculina": "masculine",
            "abreviatura": "abbreviation",
            "adversativa": "adversative",
            "afirmación": "assertion",
            "ambiguo": "ambiguous",
            "ambigua": "ambiguous",
            "auxiliar": "auxiliary",
            "causal": "causal",
            "comparativo": "comparative",
            "compuesto": "compound",
            "concesiva": "concessive",
            "condicional": "conditional",
            "conjuntiva": "conjunctive",
            "consecutiva": "consecutive",
            "coordinante": "coordinating",
            "copulativa": "copulative",
            "defectivo": "defective",
            "demostrativo": "demonstrative",
            "demostrativa": "demonstrative",
            "determinado": "definite",
            "deverbal": "deverbal",
            "dígrafo": "digraph",
            "distributiva": "distributive",
            "duda": "doubt",
            "enclítico": "enclitic",
            "enclítica": "enclitic",
            "epiceno": "epicene",
            "exclamativo": "exclamative",
            "final": "final",
            "flexivo": "inflectional",
            "impersonal": "impersonal",
            "indeclinable": "indeclinable",
            "indeterminado": "indeterminate",
            "infijo": "infix",
            "interjectiva": "interjective",
            "interrogativo": "interrogative",
            "intransitiva": "intransitive",
            "invariable": "invariable",
            "latina": "latin",
            "locativo": "locative",
            "lugar": "locative",
            "modal": "modal",
            "modo": "mode",
            "negación": "negation",
            "neutro": "neuter",
            "numeral": "numeral",
            "número": "number",
            "orden": "order",
            "partitivo": "partitive",
            "partitiva": "partitive",
            "personal": "personal",
            "plural": "plural",
            "prepositiva": "prepositive",
            "pronominal": "pronominal",
            "propia": "own",
            "propio": "own",
            "reflexivo": "reflexive",
            "relativo": "relative",
            "superlativo": "superlative",
            "tiempo": "temporal",
            "transitiva": "transitive",
            "vocativo": "vocative",
        },
        "ignore": [
            "y",
            "o",
            "e",
            "hecha",
            "de",
            "con",
            "+",
        ],
        "ban": [
            "refranes",
            "relacionados",
        ]
    }
