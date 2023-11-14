from rules.assignationrule import AssignationRule
from section import Section

class NameRule(AssignationRule):
    
    def __init__(self, name: str, processor: type, section_type: str | None):
        super().__init__(processor, section_type)
        self.name = name
        
    def evaluate(self, section: Section) -> bool:
        return self.name == section.name
