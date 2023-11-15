import json
from htmlobject import HTMLObject
from lxml.etree import _Element
from section import Section


class Page(HTMLObject):
    def __init__(self, root: _Element, lema: str) -> None:
        super().__init__(root)
        self.lema: str = lema
        root_obj = HTMLObject(root)
        self.sections: list[Section] = Section.get_inner_sections(
            root_obj, "first_sections"
        )
        print(
            f"New Page for lema {self.lema}, number of sections {len(self.sections)}"
        )  # debug

    def process(self):
        print(f"Procesing Page {self.lema}")  # debug
        res = []
        for section in self.sections:
            res.append(section.process())

        print(json.dumps(res, ensure_ascii=False, indent=2))  # debug
