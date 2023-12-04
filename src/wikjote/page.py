import json
from htmlobject import HTMLObject
from lxml.etree import ElementBase
from section import Section


class Page(HTMLObject):
    def __init__(
        self, root: ElementBase, lema: str, parent: HTMLObject | None = None
    ) -> None:
        super().__init__(root, parent)
        self.lema: str = lema
        self.name = lema
        self.logger.debug('Creating PAGE for lema "%s"', self.lema)
        self.logger.debug('Getting SECTIONS for lema "%s"', self.lema)
        self.sections: list[Section] = Section.get_inner_sections(
            self, "first_sections"
        )
        self.logger.debug(
            'PAGE for lema "%s", number of SECTIONS %d', self.lema, len(self.sections)
        )

    def process(self):
        self.logger.debug('Procesing PAGE "%s"', self.lema)
        res = []
        for section in self.sections:
            res.append(section.process())

        # print(json.dumps(res, ensure_ascii=False, indent=2))  # debug
