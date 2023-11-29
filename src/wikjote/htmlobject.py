from __future__ import annotations
import logging
from lxml.etree import ElementBase
from exceptions import XMLNotFound


class HTMLObject:
    logger: logging.Logger = logging.getLogger("wikjote")

    def __init__(self, root: ElementBase) -> None:
        self.root = root
        self.name = None

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
                # TODO content formating should be done elsewere
                # attr_content = split[1].split(",")
                # attr_content = [content.strip(" .,") for content in attr_content]
                res[attr_name] = attr_content

        return res
