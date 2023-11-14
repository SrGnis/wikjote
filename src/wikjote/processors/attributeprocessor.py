from processors.procesor import Processor
from section import Section


class AttributeProcessor(Processor):

    def __init__(self, object: Section, section_type: str):
        super().__init__(object, section_type)

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
                
        return {
            'name': self.object.name,
            'type': self.section_type,
            'contents': res,
        }
    
        