from __future__ import annotations
import logging
from lxml.etree import ElementBase

from wikjote.exceptions import XMLNotFound


class HTMLObject:
    logger: logging.Logger = logging.getLogger("wikjote")

    def __init__(self, root: ElementBase, parent: HTMLObject | None = None) -> None:
        self.root = root
        self.parent = parent
        self.name: str = "None"

    @staticmethod
    def get_all_text(
        element: ElementBase
        | HTMLObject
        | list[ElementBase]
        | list[HTMLObject]
        | list[HTMLObject | ElementBase],
    ) -> str:
        if not isinstance(element, list):
            element = [element]
        if all(isinstance(n, HTMLObject) for n in element):
            element = [i.root for i in element]
        text = ""
        for e in element:
            text += "".join(e.itertext()).strip()  # type: ignore
        return text

    def text(self) -> str:
        return self.get_all_text(self.root)

    def find(self, query: str) -> list[HTMLObject]:
        result: list[HTMLObject] = [HTMLObject(i) for i in self.root.xpath(query)]
        return result

    def find_or_fail(self, query: str) -> list[HTMLObject]:
        result = self.find(query)
        if len(result) == 0:
            raise XMLNotFound(query)
        return result

    def parse_attributes(self):
        # TODO check "Ejemplos" parsing
        contents = self.find(".//li")
        res = {}
        for content in contents:
            split = content.text().split(":")
            if len(split) == 2:
                attr_name = split[0].strip()
                attr_content = split[1].strip(" .")
                res[attr_name] = attr_content

        return res

    def stack_names(self) -> list[str]:
        if self.parent is None:
            return [self.name]
        else:
            parent_res = self.parent.stack_names()
            parent_res.append(self.name)
            return parent_res

    def stack_string(self) -> str:
        return " ".join(self.stack_names())

    def remove(self):
        self.root.getparent().remove(self.root)
