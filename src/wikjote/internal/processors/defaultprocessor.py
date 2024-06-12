from typing import Any

from wikjote.processors.procesor import Processor
from wikjote.htmlobject import HTMLObject


class DefaultProcessor(Processor):
    def run(self) -> Any:
        contents = self.object.find(
            "./child::*[not(descendant-or-self::h1 | descendant-or-self::h2 | descendant-or-self::h3 | descendant-or-self::h4 | descendant-or-self::h5 | descendant-or-self::section)]"
        )  # we dont want the name of the section or subsections
        text = HTMLObject.get_all_text(contents)
        text = text.strip(" .")
        return text
