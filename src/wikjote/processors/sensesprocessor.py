from processors.procesor import Processor
from htmlobject import HTMLObject
from section import Section
from queries import xpathqueries
from copy import deepcopy

class SensesProcessor(Processor):

    def __init__(self, object: Section):
        super().__init__(object)
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

                #if the sense has ul probably is not a sense
                if(len(sense.find('.//ul')) > 0):
                    continue

                sense_obj = {}
                try:
                    head = sense.find_or_fail(xpathqueries['sense_head'])
                    sense_obj['head'] = head.[0].text() # type: ignore
                    
                    content = sense.find_or_fail(xpathqueries['sense_content'])
                    sense_obj['content'] = content.[0].text() # type: ignore
                except:
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
            return category_obj