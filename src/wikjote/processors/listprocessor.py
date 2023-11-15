import re
from processors.procesor import Processor
from htmlobject import HTMLObject


class ListProcessor(Processor):
    def run(self):
        contents = self.object.find(".//li")
        res = []
        for content in contents:
            text = HTMLObject.get_all_text(content)
            text = re.sub("\[.*\]", "", text)
            text = text.strip(" .")
            res.append(text)
        return res
