from processors.procesor import Processor
from htmlobject import HTMLObject
from queries import xpathqueries
from section import Section

class LanguageProcessor(Processor):

    def __init__(self, object: Section):
        super().__init__(object)
        self.object: Section

    def run(self):
        elements = self.object.find(xpathqueries['inner_sections'])
        self.object.subsections = [Section(i.root) for i in elements] 