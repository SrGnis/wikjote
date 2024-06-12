from typing import Any
from lxml.etree import ElementBase

from wikjote.htmlobject import HTMLObject
import wikjote.queries as queries
from wikjote.rules.assignator import ProcessorAssignator


class Section(HTMLObject):
    """The class that repesents a Section of a Page.

    Subclass of HTMLObject.

    The objective of the class is to ease the generation and processing of a section and their subsections.

    Usually created by the static method Section.get_inner_sections().

    Attributes:
        root: The wrapped ElementBase.
        parent: The parent HTMLObject if any.
        name: The name of the object extracted from the root.
        processor: The processor associated to this section by the ProcessorAssignator.
        subsections: A list of sections inside this one.
    """

    def __init__(self, root: ElementBase, parent: HTMLObject | None = None) -> None:
        """Initializes the instance.

        The "name" is extracted from the root by the get_section_name() method.
        It calls the set_processor() method to assign a "processor" to the section.
        It also calls the get_inner_sections() method to fill the "subsections" attribute.

        Args:
            root (ElementBase): A xml element to wrapp.
            parent (HTMLObject | None, optional): The parent of this object. Defaults to None.
        """
        super().__init__(root, parent)
        self.name: str = self.get_section_name(self)
        self.logger.debug('Creating SECTION "%s"', self.name)
        self.set_processor()
        self.logger.debug('SUBSECTIONS of SECTION "%s"', self.name)
        self.subsections: list[Section] = self.get_inner_sections(self)
        self.logger.debug(
            'SECTION "%s" created, number of SUBSECTIONS %d',
            self.name,
            len(self.subsections),
        )

    def set_processor(self):
        """Sets the attribute "processor" to the result of calling ProcessorAssignator.assign() over itself."""
        self.processor = ProcessorAssignator.assign(self)
        self.logger.debug(
            'SECTION "%s" PROCESSOR: "%s" with type "%s"',
            self.name,
            self.processor.__class__.__name__,
            self.processor.section_type,
        )

    def process(self):
        """Process the section, and subsections into a dict.

        Calls the run() method of the Processor associated to get the contents
        of the section and calls process_subsections() to also process his subsections.

        Returns:
            dict: A repesentation of de section following the next schema:
            {
                "name": str,
                "type": str,
                "contents": any,
                "sub_sections": list,
            }
            The sub_sections list is composed by dicts with the same structure.
        """
        self.logger.debug(
            'PROCESSING SECTION "%s", type "%s", PROCESSOR: "%s"',
            self.name,
            self.processor.section_type,
            self.processor.__class__.__name__,
        )
        section_res = {
            "name": self.name,
            "type": self.processor.section_type,
            "contents": self.processor.run(),
        }
        section_res["sub_sections"] = self.process_subsections()

        self.logger.debug('SECTION "%s" PROCESSED', self.name)

        return section_res

    def process_subsections(self):
        """Process the subsections.

        Calls the process() method of each subsection and return a list of the results.

        Returns:
            list: A list composed by dicts with the same structure as the result of the process() method.
        """
        self.logger.debug('PROCESSING SUBSECTIONS of SECTION "%s"', self.name)
        res = []
        for section in self.subsections:
            res.append(section.process())

        return res

    @staticmethod
    def get_inner_sections(root_obj: HTMLObject, query: str | None = None, args: list[Any] = []):
        """Searches sections in the "root_obj".

        The default query is "inner_secctions".

        TODO improve the optional query.

        Args:
            root_obj (HTMLObject): The object to search.
            query (str | None, optional): A optional xpathqueries name to use instead of the default one.

        Returns:
            list[Section]: A list with the inner sections.
        """
        if query is None:
            query = "inner_sections"
        sections = root_obj.find(queries.xpathqueries[query].format(*args))
        return [Section(section.root, root_obj) for section in sections]

    @staticmethod
    def get_section_name(root_obj: HTMLObject):
        """Gets the section name using the query "section_name".

        TODO allow using other queries.

        Args:
            root_obj (HTMLObject): The object to search.

        Returns:
            str: The name of the section.
        """
        return HTMLObject.get_all_text(
            root_obj.find_or_fail(queries.xpathqueries["section_name"])[0]
        ).strip()
