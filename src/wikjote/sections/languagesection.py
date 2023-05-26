from lxml.etree import _Element
from sections.section import Section
from processors.languageprocessor import LanguageProcessor

class LanguageSection(Section):
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)

    def set_processor(self):
        self.processor = LanguageProcessor(self)