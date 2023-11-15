from processors.procesor import Processor
from section import Section
import re


class TranslationsProcessor(Processor):
    def run(self):
        contents = self.object.find(".//li")
        res = {}
        for content in contents:
            txt = Section.get_all_text(content).strip()
            txt = re.sub("\[.*\]", "", txt)  # remove [1]
            txt = re.sub("\(.*\).*", "", txt)  # remove (es)...
            txt = txt.split(":")
            if len(txt) == 2:
                res[txt[0].strip()] = txt[1].strip()
        return res
