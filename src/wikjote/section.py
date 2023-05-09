from htmlobject import HTMLObject
from lxml.etree import _Element
#from wikjote.registry import ProcessorRegistry
from wikjote.queries import xpathqueries

class Section(HTMLObject):
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)
        self.name: str = HTMLObject.get_all_text(self.find_or_fail(xpathqueries['section_name']))
        #self.processor = ProcessorRegistry.get(self.name, self)