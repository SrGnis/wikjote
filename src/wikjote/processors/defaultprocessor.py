from wikjote.processors.procesor import Processor
from wikjote.htmlobject import HTMLObject

class DefaultProcessor(Processor):

    def __init__(self, object: HTMLObject):
        super().__init__(object)

    def run(self):
        contents = self.object.find('./summary/following-sibling::*')
        return HTMLObject.get_all_text(contents).strip()