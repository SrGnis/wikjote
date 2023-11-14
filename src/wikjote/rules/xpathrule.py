import re
from rules.assignationrule import AssignationRule
from section import Section

class XPathRule(AssignationRule):
    
    def __init__(self, xpath: str, processor: type, section_type: str | None):
        super().__init__(processor, section_type)
        self.xpath = xpath
        
    def evaluate(self, section: Section) -> bool:
        return len(section.find(self.xpath)) > 0
