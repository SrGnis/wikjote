from typing import Any

from wikjote.processors.procesor import Processor
from wikjote.htmlobject import HTMLObject


class DefaultProcessor(Processor):
    def run(self) -> Any:
        contents = self.object.find(
            "./child::*[not(self::h1 | self::h2 | self::h3 | self::h4 | self::h5 | self::section)]"
        )  # we dont want the name of the section or subsections
        text = HTMLObject.get_all_text(contents)
        text = text.strip(" .")
        return text
