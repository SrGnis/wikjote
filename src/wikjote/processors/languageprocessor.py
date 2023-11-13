from processors.procesor import Processor
from queries import xpathqueries
from section import Section

class LanguageProcessor(Processor):

    def __init__(self, object: Section):
        super().__init__(object)
        self.object: Section

    def run(self):
        self.object.process_subsections()