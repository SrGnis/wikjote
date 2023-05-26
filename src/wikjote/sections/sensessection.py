from lxml.etree import _Element
from sections.section import Section
from processors.sensesprocessor import SensesProcessor

class SensesSection(Section):
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)

    def set_processor(self):
        self.processor = SensesProcessor(self)