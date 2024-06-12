from wikjote.rules.assignationrule import AssignationRule
from wikjote.section import Section


class XPathRule(AssignationRule):
    def __init__(self, processor: type, section_type: str | None, xpath: str):
        super().__init__(processor, section_type)
        self.xpath = xpath

    def evaluate(self, section: Section) -> bool:
        return section.seach_check(self.xpath)