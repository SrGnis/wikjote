from copy import deepcopy
import re

from queries import xpathqueries
from processors.procesor import Processor


class SensesProcessor(Processor):
    def run(self):
        sense_array = []
        try:
            # flection = get_flection(section, language)
            # category_obj['flection'] = flection

            senses = self.object.find(xpathqueries["senses"])
            for sense in senses:
                sense_obj = {}
                try:
                    head = sense.find_or_fail(xpathqueries["sense_head"])
                    sense_obj["head"] = head[0].text()

                    content = sense.find_or_fail(xpathqueries["sense_content"])
                    content = content[0].text()  # all the inner text
                    content = content[: content.find("\n")]  # remove attributes
                    content = re.sub("\[.*\]", "", content)  # remove refeneces
                    content = content.strip(" .")
                    sense_obj["content"] = content

                    attributes_section = sense.find(xpathqueries["sense_attributes"])
                    if len(attributes_section) > 0:
                        attributes = attributes_section[0].parse_attributes()
                        sense_obj["attributes"] = attributes

                except Exception as exception:
                    print(exception)
                    sense_obj = None
                    # check if the sense is malformated
                    has_dt = len(sense.find("./dt")) > 0
                    dd = sense.find("./dd")
                    has_dd = len(dd) > 0
                    if has_dd and not has_dt:
                        sense_array[-1]["content"] += "\n" + dd[0].text()

                if sense_obj is not None:
                    sense_array.append(deepcopy(sense_obj))

        except Exception:
            print("Error in category")

        return sense_array
