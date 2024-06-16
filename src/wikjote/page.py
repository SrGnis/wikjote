from lxml.etree import ElementBase

from wikjote.htmlobject import HTMLObject
from wikjote.section import Section


class Page(HTMLObject):
    """The class that represents a Page.

    Subclass of HTMLObject.

    The `Page` contains a list of his `Sections` and can process them into a list of dicts.

    FIXME: `name` and `lema` are redundant.

    Attributes:
        root: The wrapped `ElementBase`.
        parent: The parent `HTMLObject` if any.
        name: The name of the `Page`.
        lema: The lema of the `Page`.
        sections: A list of sections inside this one. 
    """

    def __init__(
        self, root: ElementBase, lema: str, parent: HTMLObject | None = None
    ) -> None:
        """Initializes the instance.

        The attribute sections is filled with the result of the call of `Section.get_inner_sections(self, "first_sections")`

        Args:
            root (ElementBase): A xml element to wrap.
            lema (str): The lema of the Page.
            parent (HTMLObject | None, optional): The parent of this object. Defaults to None.
        """
        super().__init__(root, parent)
        self.lema: str = lema
        self.name = lema
        self.logger.debug('Creating PAGE for lema "%s"', self.lema)
        self.logger.debug('Getting SECTIONS for lema "%s"', self.lema)
        query_args = ["Español"]
        self.sections: list[Section] = Section.get_inner_sections(
            self, "language_section_chosed", query_args
        )
        if len(self.sections) > 0:
            self.logger.debug(
                'PAGE for lema "%s", number of SECTIONS %d',
                self.lema,
                len(self.sections),
            )
        else:
            if(len(query_args) == 0):
                self.logger.warning('No SECTIONS found for PAGE of lema "%s"', self.lema)

    def process(self):
        """Process the Page and return a list of the dicts that represent the sections.

        Returns:
            list: A dict whit the page lema and list of dicts of sections, see Section.process().
        """
        self.logger.debug('Procesing PAGE "%s"', self.lema)
        res = {"page": self.lema, "sections": []}
        for section in self.sections:
            res["sections"].append(section.process())

        return res
