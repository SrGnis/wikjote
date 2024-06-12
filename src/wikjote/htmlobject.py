from __future__ import annotations
import logging
from typing import Sized
from lxml.etree import ElementBase

from wikjote.exceptions import XMLNotFound


class HTMLObject:
    """A wrapper class for lxml.etree.ElementBase with some utility methods.

    Attributes:
        root: The wrapped ElementBase.
        parent: The parent HTMLObject if any.
        name: The name of the object, Defaults to "None".
    """

    logger: logging.Logger = logging.getLogger("wikjote")

    def __init__(self, root: ElementBase, parent: HTMLObject | None = None) -> None:
        """Initializes the instance.

        Args:
            root (ElementBase): A xml element to wrapp.
            parent (HTMLObject | None, optional): The parent of this object. Defaults to None.
        """
        self.root = root
        self.parent = parent
        self.name: str = "None"

    @staticmethod
    def get_all_text(
        element: (
            ElementBase
            | HTMLObject
            | list[ElementBase]
            | list[HTMLObject]
            | list[HTMLObject | ElementBase]
        ),
    ) -> str:
        """Static method to get all the inner text on the elements.

        Args:
            element (ElementBase | HTMLObject | list[ElementBase] | list[HTMLObject] | list[HTMLObject  |  ElementBase]): Input elements to extract the inner text.

        Returns:
            str: The inner text, Defaults to "".
        """
        if not isinstance(element, list):
            element = [element]
        if all(isinstance(n, HTMLObject) for n in element):
            element = [i.root for i in element]
        text = ""
        for e in element:
            text += "".join(e.itertext()).strip()  # type: ignore
        return text

    def text(self) -> str:
        """Get the inner text of this object.

        Calls get_all_text() to get the text.

        Returns:
            str: The inner text.
        """
        return self.get_all_text(self.root)

    def find(self, query: str) -> list[HTMLObject]:
        """Returns the result of a xpath query over the element.

        Args:
            query (str): A xpath query.

        Returns:
            list[HTMLObject]: The list of found elements.
        """
        result: list[HTMLObject] = [HTMLObject(i) for i in self.root.xpath(query)]
        return result

    def find_or_fail(self, query: str) -> list[HTMLObject]:
        """Returns the result of a xpath query over the element or an error if none are found.

        Args:
            query (str): A xpath query.

        Raises:
            XMLNotFound: The xpath query found nothing.

        Returns:
            list[HTMLObject]: The list of found elements.
        """
        result = self.find(query)
        if len(result) == 0:
            raise XMLNotFound(query)
        return result
    
    def seach_check(self, query: str) -> bool:
        """Returns if the xpath query finds any result.

        Args:
            query (str): A xpath query.

        Returns:
            bool
        """
        xpath_result = self.root.xpath(query)
        if (isinstance(xpath_result, bool)):
            return xpath_result
        if (isinstance(xpath_result, Sized)):
            return (len(xpath_result) > 0)
        return False


    def parse_attributes(self):
        """Parse the elements of a atribute list of ES wiktionary.

        Given a atrribute list following this schema:

        <ul>
          <li>
            NAME: CONTENT.
          </li>
          <li>
            NAME: CONTENT.
          </li>
        </ul>

        Is parsed into a dict:

        {
          NAME: CONTENT,
          NAME: CONTENT,
        }


        Returns:
            _type_: The parsed attributes.
        """
        # TODO check "Ejemplos" parsing
        contents = self.find(".//li")
        res = {}
        for content in contents:
            split = content.text().split(":")
            if len(split) == 2:
                attr_name = str.lower(split[0].strip())
                # appling plurals
                # TODO: move this to a handler?
                if attr_name[-1] != "s":
                    attr_name = attr_name + "s"
                attr_content = split[1].strip(" .")
                res[attr_name] = attr_content

        return res

    def stack_names(self) -> list[str]:
        """Recursive method to get a list of the parents and self names.

        Returns:
            list[str]: A list with the parents and self names.
        """
        if self.parent is None:
            return [self.name]
        else:
            parent_res = self.parent.stack_names()
            parent_res.append(self.name)
            return parent_res

    def stack_string(self) -> str:
        """Get a string with the list of the parents and self names.

        Returns:
            str: A string with the list of the parents and self names.
        """
        return " ".join(self.stack_names())

    def remove(self):
        """Removes the element and his children from the etree."""
        self.root.getparent().remove(self.root)
