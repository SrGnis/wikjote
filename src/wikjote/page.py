from htmlobject import HTMLObject
from lxml.etree import _Element
from queries import xpathqueries
from section import Section
import json

class Page(HTMLObject):
    
    def __init__(self, root: _Element, lema: str) -> None:
        super().__init__(root)
        self.lema: str = lema
        root_obj = HTMLObject(root)
        self.sections: list[Section] = Section.get_inner_sections(root_obj, 'first_sections')
        print("New Page for lema {}, number of sections {}".format(self.lema,len(self.sections))) #debug
        
    def get_languajes(self):
        if(True):
            elements = self.find_or_fail(xpathqueries['language_section_chosed'].format('Español'))
        else:
            elements = self.find_or_fail(xpathqueries['language_sections'])
    
    def process(self):
        print("Procesing Page {}".format(self.lema)) #debug
        res = []
        for section in self.sections:
            res.append(section.process())
            
        print(json.dumps(res, ensure_ascii=False, indent= 2)) #debug
