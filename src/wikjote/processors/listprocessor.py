from processors.procesor import Processor
from htmlobject import HTMLObject


class ListProcessor(Processor):
    def run(self):
        contents = self.object.find(".//li")
        res = []
        for content in contents:
            res.append(HTMLObject.get_all_text(content).strip())
        return {
            "name": self.object.name,
            "type": self.section_type,
            "contents": res,
        }
