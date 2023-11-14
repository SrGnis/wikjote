from processors.procesor import Processor
from section import Section
from queries import xpathqueries
from copy import deepcopy

from processors.attributeprocessor import AttributeProcessor

class SensesProcessor(Processor):

    def __init__(self, object: Section, section_type: None | str = None):
        super().__init__(object, section_type)
        self.object: Section

    def run(self):
        category_obj = {}
        try:
            category_obj['type'] = self.object.name
            
            #flection = get_flection(section, language)
            #category_obj['flection'] = flection
            
            senses = self.object.find(xpathqueries['senses'])
            sense_array = []
            for sense in senses:
                
                # print(sense.text()) #debug

                # TODO: senses can have ul to specify attributes, parse those correctly
                # WRONG: if the sense has ul probably is not a sense
                # if(len(sense.find('.//ul')) > 0):
                #     continue

                sense_obj = {}
                try:
                    head = sense.find_or_fail(xpathqueries['sense_head'])
                    sense_obj['head'] = head[0].text() # type: ignore
                    
                    content = sense.find_or_fail(xpathqueries['sense_content'])
                    sense_obj['content'] = content[0].text() # type: ignore
                    
                    attributes_section = sense.find(xpathqueries['sense_attributes'])
                    if(len(attributes_section)>0):
                        sense_obj['attributes'] = AttributeProcessor(attributes_section[0]).run()
                except Exception as e:
                    print(e)
                    sense_obj = None
                    # check if the sense is malformated
                    has_dt = len(sense.find('./dt')) > 0
                    dd = sense.find('./dd')
                    has_dd = len(dd) > 0
                    if(has_dd and not has_dt):
                        sense_array[-1]["content"] += '\n' + dd[0].text()
                    
                
                if(sense_obj != None):
                    sense_array.append(deepcopy(sense_obj))
                
            category_obj['senses'] = sense_array
            
        except Exception as e:
            print('Error in category:', self.object.name)
        finally:
            return {
            'name': self.object.name,
            'type': self.section_type,
            'contents': category_obj,
        }