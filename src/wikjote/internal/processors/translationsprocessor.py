from typing import Any
import re

from processors.procesor import Processor
from section import Section


class TranslationsProcessor(Processor):
    def run(self) -> Any:
        contents = self.object.find(".//li")
        res = {}
        for content in contents:
            txt = Section.get_all_text(content).strip()
            txt = re.sub(r"\s*\(.+\).*,", ",", txt)  # remove (es),
            txt = re.sub(r"\s*\(.+\).*", "", txt)  # remove (es)
            txt = re.sub(r"\s\s", " ", txt)  # remove doble spaces,
            txt = txt.split(":")
            if len(txt) == 2:
                res[txt[0].strip()] = txt[1].strip()
        return res
