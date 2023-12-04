from typing import Any
from copy import deepcopy
import re

from queries import xpathqueries
from processors.procesor import Processor
from utils.tableparser import parse_table


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

            senses = self.object.find(xpathqueries["senses"])
            for index, sense in enumerate(senses):
                # //details[child::dl]/dl[@id="this"]/following-sibling::ul[count(preceding-sibling::dl)={index}]
                sense_obj = {}

                sense_obj["title"] = None
                head = sense.find(xpathqueries["sense_title"])
                if len(head) > 0:
                    sense_obj["title"] = head[0].text()

                sense_obj["content"] = None
                content = sense.find(xpathqueries["sense_content"])
                if len(content) > 0:
                    # first process atributes and remove them
                    sense_obj["attributes"] = {}
                    attributes_sections = sense.find(xpathqueries["sense_attributes"])
                    for attribute_section in attributes_sections:
                        attributes = attribute_section.parse_attributes()
                        sense_obj["attributes"] = sense_obj["attributes"] | attributes
                        attribute_section.remove()

                    attributes_sections_wrong = sense.find(
                        xpathqueries["sense_attributes_wrong"].format(index + 1)
                    )
                    for attribute_section in attributes_sections_wrong:
                        self.logger.warning(
                            'Malformated attribute corrected in "%s"',
                            self.object.stack_string(),
                        )
                        attributes = attribute_section.parse_attributes()
                        sense_obj["attributes"] = sense_obj["attributes"] | attributes
                        attribute_section.remove()

                    content = content[0].text()
                    content = re.sub(r"\[.*\]", "", content)  # remove refeneces
                    content = content.strip(" .")
                    if content != "":
                        sense_obj["content"] = content

                if sense_obj is not {}:
                    sense_array.append(deepcopy(sense_obj))
                    if sense_obj["title"] is None:
                        self.logger.warning(
                            'Sense without title in "%s"', self.object.stack_string()
                        )
                    if sense_obj["content"] is None:
                        self.logger.warning(
                            'Sense without content in "%s"', self.object.stack_string()
                        )

            res["senses"] = sense_array
            res["inflection"] = inflection

            if len(sense_array) == 0:
                # TODO: show lema and upper sections
                self.logger.warning(
                    'No senses found in "%s"', self.object.stack_string()
                )

        except Exception:
            # TODO: show lema and upper sections
            self.logger.exception(
                'Error getting senses of "%s"', self.object.stack_string()
            )

        return res
