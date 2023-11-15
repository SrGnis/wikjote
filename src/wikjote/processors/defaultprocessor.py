from processors.procesor import Processor
from htmlobject import HTMLObject


class DefaultProcessor(Processor):
    def run(self):
        contents = self.object.find("./summary/following-sibling::*")
        return {
            "name": self.object.name,
            "type": self.section_type,
            "contents": HTMLObject.get_all_text(contents).strip(),
        }
