from processors.procesor import Processor
from htmlobject import HTMLObject

class ListProcessor(Processor):

    def __init__(self, object: HTMLObject):
        super().__init__(object)

    def run(self):
        contents = self.object.find( './/li')
        res = []
        for content in contents:
            res.append(HTMLObject.get_all_text(content).strip())
        return res