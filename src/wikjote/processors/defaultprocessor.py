from processors.procesor import Processor
from htmlobject import HTMLObject

class DefaultProcessor(Processor):

    def __init__(self, object: HTMLObject):
        super().__init__(object)

    def run(self):
        contents = self.object.find('./summary/following-sibling::*')
        return HTMLObject.get_all_text(contents).strip()