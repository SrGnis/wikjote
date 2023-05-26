from lxml.etree import _Element
from sections.section import Section
from processors.defaultprocessor import DefaultProcessor

class EtymologySection(Section):
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)

    def set_processor(self):
        self.processor = DefaultProcessor(self)