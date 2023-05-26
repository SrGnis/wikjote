from htmlobject import HTMLObject
from lxml.etree import _Element
import queries
from processors.defaultprocessor import DefaultProcessor

class Section(HTMLObject):

    fallback_processor = DefaultProcessor
    
    def __init__(self, root: _Element) -> None:
        super().__init__(root)
        self.subsections: list[Section] = []
        self.name: str = HTMLObject.get_all_text(self.find_or_fail(queries.xpathqueries['section_name']))
        self.set_processor()

    def set_processor(self):
        self.processor = DefaultProcessor(self)

    def process(self):
        #TODO: try except
        return self.processor.run()
        
    def process_subsections(self):
        res = []
        for section in self.subsections:
            res.append((section.name, section.process()))
