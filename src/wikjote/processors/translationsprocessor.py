from processors.procesor import Processor
from htmlobject import HTMLObject
import re

class TranslationsProcessor(Processor):

    def __init__(self, object: HTMLObject):
        super().__init__(object)

    def run(self):
        contents = self.object.find('.//li')
        res = {}
        for content in contents:
            txt = HTMLObject.get_all_text(content).strip()
            txt = re.sub('\[.*\]', '', txt)# remove [1]
            txt = re.sub('\(.*\).*', '', txt)# remove (es)...
            txt = txt.split(':')
            if(len(txt) == 2):
                res[txt[0].strip()] = txt[1].strip()
        return res