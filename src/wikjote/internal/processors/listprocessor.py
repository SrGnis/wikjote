from typing import Any
import re

from wikjote.processors.procesor import Processor
from wikjote.htmlobject import HTMLObject


class ListProcessor(Processor):
    def run(self) -> Any:
        contents = self.object.find(".//li")
        res = []
        for content in contents:
            text = HTMLObject.get_all_text(content)
            # text = re.sub(r"\[.*\]", "", text)
            text = text.strip(" .")
            res.append(text)
        return res
