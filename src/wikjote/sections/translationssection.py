from lxml.etree import _Element
from sections.section import Section
from processors.translationsprocessor import TranslationsProcessor

class TranslationsSection(Section):
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)

    def set_processor(self):
        self.processor = TranslationsProcessor(self)