import json

from htmlobject import HTMLObject
from lxml.etree import ElementBase
import queries
from rules.assignator import ProcessorAssignator


class Section(HTMLObject):
    def __init__(self, root: ElementBase, parent: HTMLObject | None = None) -> None:
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
        self.processor = ProcessorAssignator.assign(self)
        self.logger.debug(
            'SECTION "%s" PROCESSOR: "%s" with type "%s"',
            self.name,
            self.processor.__class__.__name__,
            self.processor.section_type,
        )

    def process(self):
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
        self.logger.debug('PROCESSING SUBSECTIONS of SECTION "%s"', self.name)
        res = []
        for section in self.subsections:
            res.append(section.process())

        return res

    @staticmethod
    def get_inner_sections(root_obj: HTMLObject, query: str | None = None):
        if query is None:
            query = "inner_sections"
        sections = root_obj.find(queries.xpathqueries[query])
        return [Section(section.root, root_obj) for section in sections]

    @staticmethod
    def get_section_name(root_obj: HTMLObject):
        # TODO generlalize
        return HTMLObject.get_all_text(
            root_obj.find_or_fail(queries.xpathqueries["section_name"])[0]
        ).strip()
