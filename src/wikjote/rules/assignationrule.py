from wikjote.processors.procesor import Processor


class AssignationRule:
    def __init__(self, processor: type[Processor], section_type: str | None):
        self.processor = processor
        self.type = section_type

    def evaluate(self, section: "Section") -> bool:  # type: ignore
        return False
