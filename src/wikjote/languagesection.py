from htmlobject import HTMLObject
from lxml.etree import _Element
from registry import ProcessorRegistry
import queries

class Section(HTMLObject):
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)
        self.subsections: list[Section] = []
        self.name: str = HTMLObject.get_all_text(self.find_or_fail(queries.xpathqueries['section_name']))
        self.set_processor()

    def set_processor(self):
        self.processor = ProcessorRegistry.get(self.name, self)