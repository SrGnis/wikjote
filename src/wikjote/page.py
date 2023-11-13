from htmlobject import HTMLObject
from lxml.etree import _Element
from queries import xpathqueries
from section import Section

class Page(HTMLObject):
    
    def __init__(self, root: _Element, lema: str) -> None:
        super().__init__(root)
        self.lema: str = lema
        root_obj = HTMLObject(root)
        self.sections: list[Section] = Section.get_inner_sections(root_obj, 'language_sections')
        
    def get_languajes(self):
        if(True):
            elements = self.find_or_fail(xpathqueries['language_section_chosed'].format('Español'))
        else:
            elements = self.find_or_fail(xpathqueries['language_sections'])
    
    def process(self):
        print(len(self.sections))
        for section in self.sections:
            print(section.name, section.processor.__class__)
            section.process()