from processors.procesor import Processor
from htmlobject import HTMLObject

class AttributeProcessor(Processor):

    def __init__(self, object: HTMLObject):
        super().__init__(object)

    def run(self):
        contents = self.object.find( './/li')
        res = {}
        for content in contents:
            split = content.text().split(':')
            if(len(split) == 2):
                attr_name = split[0].strip()
                attr_content = split[1].split(',')
                if(len(split) == 1):
                    attr_content = split[1].strip()
                else:
                    attr_content = [content.strip() for content in attr_content]
                res[attr_name] = attr_content
                
        return res
    
        