from typing import Any
from copy import deepcopy
import re

from wikjote.queries import xpathqueries
from wikjote.processors.procesor import Processor
from wikjote.utils.tableparser import parse_table


class SensesProcessor(Processor):
    def run(self) -> Any:
        res = {}
        try:
            sense_array = []
            inflection = None
            try:
                inflection = parse_table(self.object.root)
            except Exception:
                self.logger.error(
                    'Error getting flection table in "%s"', self.object.stack_string()
                )

            sense_obj: dict[str, Any] = {
                "title": None,
                "content": None,
                "attributes": {}
            }
            senses_elements = self.object.find(xpathqueries["senses_elements"])
            for index, element in enumerate(senses_elements):

                if (element.root.tag == "dt"):
                    if (sense_obj["title"] is not None): # if we already have a title means that a new sense has started, so we store it and clean it

                        sense_array.append(deepcopy(sense_obj))

                        if sense_obj["content"] is None:
                            self.logger.warning(
                                'Sense without content in "%s"', self.object.stack_string()
                            )
                        
                        sense_obj = {
                            "title": None,
                            "content": None,
                            "attributes": {}
                        }

                    sense_obj["title"] = element.text()

                elif (element.root.tag == "dd"):
                    attributes_sections = element.find("./ul")
                    for attribute_section in attributes_sections:
                        attributes = attribute_section.parse_attributes()
                        sense_obj["attributes"] = sense_obj["attributes"] | attributes
                        attribute_section.remove()
                    
                    quotes = element.find("./*[descendant::blockquote]")
                    if len(quotes) > 0:
                        for quote in quotes:
                            ejemplos = sense_obj["attributes"].get("ejemplos")
                            if ejemplos is None or ejemplos == "":
                                sense_obj["attributes"]["ejemplos"] = []
                            elif isinstance(ejemplos, str):
                                sense_obj["attributes"]["ejemplos"] = [ejemplos]        

                            sense_obj["attributes"]["ejemplos"].append(quote.text())
                            quote.remove()
                    
                    content = element.text()
                    content = content.strip(" .")
                    if content != "":
                        if sense_obj["content"] is None:
                            sense_obj["content"] = content
                        else:
                            self.logger.warning(
                                'Multiple sense content in "%s"', self.object.stack_string()
                            )
                
            sense_array.append(deepcopy(sense_obj))

            if sense_obj["content"] is None:
                self.logger.warning(
                    'Sense without content in "%s"', self.object.stack_string()
                )

            res["senses"] = sense_array
            res["inflection"] = inflection

            if len(sense_array) == 0:
                self.logger.warning(
                    'No senses found in "%s"', self.object.stack_string()
                )

        except Exception:
            self.logger.exception(
                'Error getting senses of "%s"', self.object.stack_string()
            )

        return res
