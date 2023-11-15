import json

from htmlobject import HTMLObject
from lxml.etree import ElementBase
import queries
from rules.assignator import ProcessorAssignator


class Section(HTMLObject):
    def __init__(self, root: ElementBase) -> None:
        super().__init__(root)
        root_obj = HTMLObject(root)
        self.name: str = self.get_section_name(root_obj)
        self.subsections: list[Section] = self.get_inner_sections(root_obj)
        self.set_processor()

    def set_processor(self):
        self.processor = ProcessorAssignator.assign(self)

    def process(self):
        print(
            f"Procesing Section {self.name}, type {self.processor.section_type}, with {self.processor.__class__.__name__}"
        )  # debug
        section_res = {
            "name": self.name,
            "type": self.processor.section_type,
            "contents": self.processor.run(),
        }
        print(f"Procesing Sub Sections {self.name}")  # debug
        section_res["sub_sections"] = self.process_subsections()

        return section_res

    def process_subsections(self):
        res = []
        for section in self.subsections:
            res.append(section.process())

        return res
        # print(json.dumps(res, ensure_ascii=False, indent= 2)) #debug

    @staticmethod
    def get_inner_sections(root_obj: HTMLObject, query: str | None = None):
        if query is None:
            query = "inner_sections"
        sections = root_obj.find(queries.xpathqueries[query])
        return [Section(section.root) for section in sections]

    @staticmethod
    def get_section_name(root_obj: HTMLObject):
        return HTMLObject.get_all_text(
            root_obj.find_or_fail(queries.xpathqueries["section_name"])[0]
        ).strip()
