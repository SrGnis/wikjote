from lxml.etree import _Element
from sections.section import Section
from processors.listprocessor import ListProcessor

class SeeMoreSection(Section):
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)

    def set_processor(self):
        self.processor = ListProcessor(self)