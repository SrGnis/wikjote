from htmlobject import HTMLObject
from lxml.etree import _Element
from queries import xpathqueries
from sections.languagesection import LanguageSection

class Page(HTMLObject):
    
    def __init__(self, root: _Element, lema: str) -> None:
        super().__init__(root)
        self.lema: str = lema
        self.languajes: dict[str, LanguageSection] = self.get_languajes()
        
    #TODO: remove not wanted sections? Ej. 'Referencias y notas'
    def get_languajes(self):
        elements = self.find_or_fail(xpathqueries['language_sections'])
        sections = [LanguageSection(element.root) for element in elements]
        return {section.name: section for section in sections}
    
    def process(self):
        for language_key in self.languajes.keys():
            language = self.languajes[language_key]
            language.process()
            language.process_subsections()