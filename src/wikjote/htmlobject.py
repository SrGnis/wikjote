from __future__ import annotations
from lxml.etree import _Element
from wikjote.exceptions import XMLNotFound
from wikjote.queries import xpathqueries

class HTMLObject:
    
    @staticmethod
    def get_all_text(element: _Element | HTMLObject | list[_Element] | list[HTMLObject] | list[HTMLObject|_Element]) -> str:
        if not isinstance(element, list): element = [element]
        if all(isinstance(n, HTMLObject) for n in element): element = [i.root for i in element]
        text = ''
        for e in element:
            text += ''.join(e.itertext()).strip() # type: ignore
        return text
    
    def __init__(self, root: _Element) -> None:
        self.root = root
        
    def text(self) -> str:
        return self.get_all_text(self.root)
        
    def find(self, query: str) -> list[HTMLObject]:
        result: list[HTMLObject] = [HTMLObject(i) for i in self.root.xpath(query)]
        return result
    
    def find_or_fail(self, query: str) -> list[HTMLObject]:
        result = self.find(query)
        if(len(result) == 0):
            raise XMLNotFound(query)
        return result
    
    #TODO: move this to a general function/processor
    def get_section_name(self):
        return self.get_all_text(self.find_or_fail(xpathqueries['section_name'])[0]).strip()