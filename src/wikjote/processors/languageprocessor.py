from processors.procesor import Processor
from section import Section

class LanguageProcessor(Processor):

    def __init__(self, object: Section, section_type: str):
        super().__init__(object, section_type)
        self.object: Section

    def run(self):
        return {
            'name': self.object.name,
            'type': self.section_type,
            'contents': None,
        }