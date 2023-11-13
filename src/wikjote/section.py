from htmlobject import HTMLObject
from lxml.etree import _Element
import queries
from processors.defaultprocessor import DefaultProcessor
import json
from registry import ProcessorRegistry 

class Section(HTMLObject):

    fallback_processor = DefaultProcessor
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)
        root_obj = HTMLObject(root)
        self.name: str = self.get_section_name(root_obj)
        self.subsections: list[Section] = self.get_inner_sections(root_obj)
        self.set_processor()

    def set_processor(self):
        self.processor = ProcessorRegistry.get(self.name, self.root)

    def process(self):
        section_res = self.processor.run() # {name, type, contents} TODO set type in Rules
        section_res['sub_sections'] = self.process_subsections()
        
        
    def process_subsections(self):
        res = []
        for section in self.subsections:
            res.append(section.process())
        
        return res
        #print(json.dumps(res, ensure_ascii=False, indent= 2)) #debug
        
    @staticmethod    
    def get_inner_sections(root_obj: HTMLObject, query: str | None = None):
        if(query == None): query = 'inner_sections'
        sections = root_obj.find(queries.xpathqueries[query])
        return [Section(section.root) for section in sections]
    
    @staticmethod
    def get_section_name(root_obj: HTMLObject):
        return HTMLObject.get_all_text(root_obj.find_or_fail(queries.xpathqueries['section_name'])[0]).strip()
