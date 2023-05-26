from processors.procesor import Processor
from queries import xpathqueries
from sections.section import Section
from registry import SectionRegistry

class LanguageProcessor(Processor):

    def __init__(self, object: Section):
        super().__init__(object)
        self.object: Section

    def run(self):
        elements = self.object.find(xpathqueries['inner_sections'])
        self.object.subsections = [SectionRegistry.get(i) for i in elements] 