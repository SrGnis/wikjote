from wikjote.rules.assignationrule import AssignationRule
from wikjote.section import Section


class NameRule(AssignationRule):
    def __init__(self, processor: type, section_type: str | None, name: str):
        super().__init__(processor, section_type)
        self.name = name

    def evaluate(self, section: Section) -> bool:
        return self.name == section.name
