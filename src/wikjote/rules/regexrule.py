import re

from wikjote.rules.assignationrule import AssignationRule
from wikjote.section import Section


class RegEx(AssignationRule):
    def __init__(
        self, regex: str, field: str, processor: type, section_type: str | None
    ):
        super().__init__(processor, section_type)
        self.regex = regex
        self.field = field

    def evaluate(self, section: Section) -> bool:
        return bool(re.search(self.regex, getattr(section, self.field)))
