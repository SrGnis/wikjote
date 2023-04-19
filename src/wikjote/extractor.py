import copy
import config
from exceptions import XMLNotFound
from lxml import etree
from lxml.etree import _Element
from queries import xpathqueries
from libzim.reader import Archive
import json

def find_or_fail(html: _Element, query: str):
    result = find(html, query)
    if(len(result) == 0):
        raise XMLNotFound(query)
    return result

def find(html: _Element, query: str):
    result: list[_Element] = html.xpath(query)
    return result
    

def process_zim():
    print("Processing zim")
    
    zim = Archive(config.zimfile)
    lema = "abrir"
    entry = zim.get_entry_by_path(lema)
    page = bytes(entry.get_item().content).decode("UTF-8")
    
    html: _Element = etree.HTML(page) # type: ignore
    
    # get the Español section
    es_section = find_or_fail(html, xpathqueries['es_section']).pop()
    categories = find(es_section, xpathqueries['categories'])
    locutions = find(es_section, xpathqueries['locutions'])
    additional_info = find(es_section, xpathqueries['additional_info'])
    tranlations = find(es_section, xpathqueries['tranlations'])
    conjugation = find(es_section, xpathqueries['conjugation'])
    
    entry_obj = {}
    
    entry_obj['lema'] = lema
    
    category_array = []
    for category in categories:
        category_obj = {}
        
        cat = find_or_fail(category, xpathqueries['category'])
        category_obj['type'] = ''.join(cat[0].itertext()) # type: ignore
        
        flection = get_flection(category, es_section)
        category_obj['flection'] = flection
        
        senses = find(category, xpathqueries['senses'])
        sense_array = []
        for sense in senses:
            sense_obj = {}
            try:
                head = find_or_fail(sense, xpathqueries['sense_head'])
                sense_obj['head'] = ''.join(head[0].itertext()) # type: ignore
                
                content = find_or_fail(sense, xpathqueries['sense_content'])
                sense_obj['content'] = ''.join(content[0].itertext()) # type: ignore
            except:
                print("WARNING: ERROR ON PARSING SENSES")
                sense_obj = None
                # check if the sense is malformated
                has_dt = len(find(sense, './dt')) > 0
                dd = find(sense, './dd')
                has_dd = len(dd) > 0
                if(has_dd and not has_dt):
                    print("INFO: MALAFORMATED SENSE, APPENDING TO LAST SENSE")
                    sense_array[-1]["content"] += '\n' + get_all_text(dd[0])
                
            
            if(sense_obj != None):
                sense_array.append(copy.deepcopy(sense_obj))
            
        category_obj['senses'] = sense_array
        
        category_array.append(copy.deepcopy(category_obj))
    
    entry_obj['categories'] = category_array
    
    if(len(conjugation) > 0):
        conjugation = get_flection(conjugation[0], es_section)
        entry_obj['conjugation'] = conjugation
    
    result = json.dumps(entry_obj, ensure_ascii=False, indent=2)
    
    print(result)


def get_flection(category, es_section):
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
    flection_table = find(category, xpathqueries['flection'])
    if len(flection_table) > 0:
        rows = find(flection_table[0], './/tr') # type: ignore
        
        flection_obj = {}
        target_level = []
        top_headers = []

        num_cols = normalize_rows(rows, row_skips, sublevels)
        print(sublevels)
        
        for row_index, row in enumerate(rows):

            #Remove sub level
            if(rm_sublevel.get(row_index,None) != None):
                sublevel = rm_sublevel[row_index]
                target_level = target_level[:target_level.index(sublevel['name'])]
                target = get_dict_level(flection_obj, target_level)
                clear = sublevel.get('clear', False)
                if(clear):
                    top_headers = []

            #Add sub level
            if(sublevels.get(row_index,None) != None):
                sublevel = sublevels[row_index]
                target = get_dict_level(flection_obj, target_level)
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
                print('ROW', row_index, 'COL', col_index, 'headers', top_headers)
                target = get_dict_level(flection_obj, target_level)
                if(True):
                    element: _Element = row_children[col_index]
                    
                    if(element.tag == 'th'):
                        row_has_th = True
                        if(col_index <= len(top_headers)-1):
                            if(col_index == 0):
                                top_headers[col_index] = get_all_text(element)
                            else:
                                top_headers[col_index] += "," + get_all_text(element)
                        else:
                            top_headers.insert(col_index, get_all_text(element))
                    if(element.tag == 'td'):
                        if(row_has_th):
                            header = ','.join([top_headers[0], top_headers[col_index]])
                        else:
                            header = ','.join([top_headers[col_index]])
                            
                        dict_content = target.get(header, None)
                        if(dict_content == None):
                            target[header] =  [get_all_text(element)]
                        else:
                            content = get_all_text(element)
                            if content not in dict_content:
                                target[header].append(content)
    return flection_obj

# TODO: rowspan CAUTION colspan should be normalized before normalizing rowspans
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

def get_all_text(element: _Element) -> str:
    return ''.join(element.itertext()) # type: ignore

# Process the first row of a table, it asumes that is composed fully by th 
def process_table_header_row(row: _Element):
    ths = find_or_fail(row,'./th')
    colspan_sum = 0
    for th in ths:
        colspan = th.get('colspan')
        if(colspan != None):
            colspan_sum += int(colspan)-1
    num_cols: int = len(ths)+colspan_sum
    row_spans: list[tuple[int,str]|None] = [None]*num_cols
    
    return num_cols, row_spans

def get_dict_level(dict_obj, levels):
    target = dict_obj
    try:
        for level in levels:
            target = target[level]
    except:
        target = dict_obj
    return target