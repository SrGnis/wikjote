class AssignationRule:
    def __init__(self, processor: type, section_type: str | None):
        self.processor = processor
        self.type = section_type

    def evaluate(self, section: "Section") -> bool:
        return False
