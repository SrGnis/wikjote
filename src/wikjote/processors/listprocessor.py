from processors.procesor import Processor
from section import Section

class ListProcessor(Processor):

    def __init__(self, object: Section, section_type: None | str = None):
        super().__init__(object, section_type)

    def run(self):
        contents = self.object.find( './/li')
        res = []
        for content in contents:
            res.append(Section.get_all_text(content).strip())
        return {
            'name': self.object.name,
            'type': self.section_type,
            'contents': res,
        }