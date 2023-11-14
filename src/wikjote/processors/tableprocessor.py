from processors.procesor import Processor
from section import Section
from lxml.etree import _Element
from queries import xpathqueries

class TableProcessor(Processor):

    def __init__(self, object: Section, section_type: None | str = None):
        super().__init__(object, section_type)

    def run(self):
        row_skips = [8,9,15,21,22,26,32,35] # rows that should not be processed
        sublevels ={
            8:{
                'name': 'indicativo',
                'end': 21,
                'clear': False
            },
            21:{
                'name': 'subjuntivo',
                'end': 32,
                'clear': False
            },
            32:{
                'name': 'imperativo',
            }
        }
        rm_sublevel = {} # auxiliar dict to help remove sublevels when a row is reached
        flection_obj = None
        flection_table = self.object.find(xpathqueries['flection'])
        if len(flection_table) > 0:
            rows = find(flection_table[0], './/tr') # type: ignore
            
            flection_obj = {}
            target_level = []
            top_headers = []

            num_cols = self.normalize_rows(rows, row_skips, sublevels)
            
            for row_index, row in enumerate(rows):

                #Remove sub level
                if(rm_sublevel.get(row_index,None) != None):
                    sublevel = rm_sublevel[row_index]
                    target_level = target_level[:target_level.index(sublevel['name'])]
                    target = self.get_dict_level(flection_obj, target_level)
                    clear = sublevel.get('clear', False)
                    if(clear):
                        top_headers = []

                #Add sub level
                if(sublevels.get(row_index,None) != None):
                    sublevel = sublevels[row_index]
                    target = self.get_dict_level(flection_obj, target_level)
                    target[sublevel['name']] = {}
                    target_level.append(sublevel['name'])
                    end = sublevel.get('end',None)
                    if(end != None):
                        rm_sublevel[end] = sublevel

                if(row_index in row_skips):
                    continue
                
                row_children = row.getchildren()
                row_has_th = False
                
                # iterate over the children of each row using num_cols to take care of the cells with rowspan
                for col_index in range(len(row_children)):
                    target = self.get_dict_level(flection_obj, target_level)
                    if(True):
                        element: _Element = row_children[col_index]
                        
                        if(element.tag == 'th'):
                            row_has_th = True
                            if(col_index <= len(top_headers)-1):
                                if(col_index == 0):
                                    top_headers[col_index] = self.object.get_all_text(element)
                                else:
                                    top_headers[col_index] += "," + self.object.get_all_text(element)
                            else:
                                top_headers.insert(col_index, self.object.get_all_text(element))
                        if(element.tag == 'td'):
                            if(row_has_th):
                                header = ','.join([top_headers[0], top_headers[col_index]])
                            else:
                                header = ','.join([top_headers[col_index]])
                                
                            dict_content = target.get(header, None)
                            if(dict_content == None):
                                target[header] =  [self.object.get_all_text(element)]
                            else:
                                content = self.object.get_all_text(element)
                                if content not in dict_content:
                                    target[header].append(content)
        return flection_obj

    # TODO: rowspan CAUTION colspan should be normalized before normalizing rowspans
    @staticmethod
    def normalize_rows(rows: list[_Element], row_skips: list[int], sublevels: dict):
        last_sublevel = None
        num_cols = len(find(rows[0], './*[self::th | self::td]')) + sum( int(e.get('colspan','1'))-1 for e in find(rows[0], './*[@colspan]'))
        for row_index, row in enumerate(rows):
            with_colspan = find(row, './*[@colspan]')
            for element in with_colspan:
                colspan = int(element.get('colspan','1'))
                element.attrib.pop('colspan')
                if(len(with_colspan) < num_cols and colspan == num_cols):
                    if row_index not in row_skips: 
                        row_skips.append(row_index)
                        #TODO: add sublevels
                        sublevels[row_index]={
                            'name': get_all_text(row).strip(),
                            'clear': True
                        }
                        if(last_sublevel != None):
                            sublevels[last_sublevel]['end'] = row_index
                        last_sublevel = row_index
                    break
                for i in range(colspan-1):
                    element.addnext(copy.deepcopy(element))
        for row_index, row in enumerate(rows):
            elements = find(row, './*[self::th | self::td]')
            for col_index, element in enumerate(elements):
                if(element.get('rowspan', None) != None):
                    rowspan = int(element.get('rowspan', None))
                    element.attrib.pop('rowspan')
                    for offset in range(rowspan-1):
                        rows[row_index+offset+1].insert(col_index, copy.deepcopy(element))
        return num_cols
    
    @staticmethod
    def get_dict_level(dict_obj, levels):
        target = dict_obj
        try:
            for level in levels:
                target = target[level]
        except:
            target = dict_obj
        return target