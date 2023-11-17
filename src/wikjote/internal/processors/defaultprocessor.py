from typing import Any
import re
from processors.procesor import Processor
from htmlobject import HTMLObject


class DefaultProcessor(Processor):
    def run(self) -> Any:
        contents = self.object.find("./summary/following-sibling::*")
        text = HTMLObject.get_all_text(contents)
        text = re.sub(r"\[.*\]", "", text)
        text = text.strip(" .")
        return text
