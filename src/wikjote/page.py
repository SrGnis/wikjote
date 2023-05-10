from htmlobject import HTMLObject
from lxml.etree import _Element
from queries import xpathqueries
from section import Section

class Page(HTMLObject):
    
    def __init__(self, root: _Element, lema: str) -> None:
        super().__init__(root)
        self.lema: str = lema
        self.languajes: dict[str, Section] = self.get_languajes()
        
    #TODO: remove not wanted sections? Ej. 'Referencias y notas'
    def get_languajes(self):
        elements = self.find_or_fail(xpathqueries['language_sections'])
        sections = [Section(element.root) for element in elements]
        return {section.name: section for section in sections}