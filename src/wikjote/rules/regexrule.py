import re

from wikjote.rules.assignationrule import AssignationRule
from wikjote.section import Section


class RegExRule(AssignationRule):
    def __init__(
        self, processor: type, section_type: str | None, field: str, regex: str
    ):
        super().__init__(processor, section_type)
        self.regex = regex
        self.field = field

    def evaluate(self, section: Section) -> bool:
        return bool(re.search(self.regex, getattr(section, self.field)))
