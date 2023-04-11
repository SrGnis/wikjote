import copy
import config
from exceptions import XMLNotFound
from lxml import etree
from lxml.etree import _Element
from queries import xpathqueries
from libzim.reader import Archive
import json

import pandas as pd
from io import StringIO 

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
    lema = "rojo"
    entry = zim.get_entry_by_path(lema)
    page = bytes(entry.get_item().content).decode("UTF-8")
    
    html: _Element = etree.HTML(page) # type: ignore
    
    # get the Español section
    es_section = find_or_fail(html, xpathqueries['es_section']).pop()
    categories = find(es_section, xpathqueries['categories'])
    locutions = find(es_section, xpathqueries['locutions'])
    additional_info = find(es_section, xpathqueries['additional_info'])
    tranlations = find(es_section, xpathqueries['tranlations'])
    
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
                    print("INFO: MLAFORMATED SENSE, APPENDING TO LAST SENSE")
                    sense_array[-1]["content"] += '\n' + get_all_text(dd[0])
                
            
            if(sense_obj != None):
                sense_array.append(copy.deepcopy(sense_obj))
            
        category_obj['senses'] = sense_array
        
        category_array.append(copy.deepcopy(category_obj))
    
    entry_obj['categories'] = category_array
    
    result = json.dumps(entry_obj, ensure_ascii=False, indent=2)
    
    print(result)


def get_flection(category, es_section):
    flection_obj = None
    flection_table = find(category, xpathqueries['flection'])
    if len(flection_table) > 0:
        
        print("FLECTION TABLE FOUND")
        
        rows = find(flection_table[0], './/tr') # type: ignore
        
        flection_obj = {}
        top_headers = []
        row_spans = []
        num_cols = None
        
        for row_index, row in enumerate(rows):
            
            print("Row:", row_index)
            
            if(num_cols == None):
                num_cols, row_spans = process_table_header_row(row)
                print("Number of colums:", num_cols)
            
            row_children = row.getchildren()
            row_has_th = False
            
            # iterate over the children of each row using num_cols to take care of the cells with rowspan
            for col_index in range(num_cols):
                
                if(row_spans[col_index]==None):
                    element: _Element = row_children[col_index]
                    
                    if(element.tag == 'th'):
                        row_has_th = True
                        if(col_index <= len(top_headers)-1):
                            top_headers[col_index] = get_all_text(element)
                        else:
                            top_headers.insert(col_index, get_all_text(element))
                    if(element.tag == 'td'):
                        
                        if(row_has_th):
                            header = ','.join([top_headers[0], top_headers[col_index]])
                        else:
                            header = ','.join([top_headers[col_index]])
                        
                        row_span = element.get('rowspan')
                        if(row_span != None):
                            row_spans[col_index] = (int(row_span), get_all_text(element)) # type: ignore
                            
                        if(row_spans[col_index] != None):
                            flection_obj[header] = row_spans[col_index][1]
                            print(col_index, header, row_spans[col_index][1]) # type: ignore
                            row_spans[col_index] = (row_spans[col_index][0]-1, row_spans[col_index][1]) # type: ignore
                            if(row_spans[col_index][0] <= 0): # type: ignore
                                row_spans[col_index] = None
                        else:
                            flection_obj[header] =  get_all_text(element)
                            print(col_index, header, get_all_text(element))
                else:
                    if(row_has_th):
                        header = ','.join([top_headers[0], top_headers[col_index]])
                    else:
                        header = ','.join([top_headers[col_index]])
                    
                    flection_obj[header] = row_spans[col_index][1]
                    print(col_index, header, row_spans[col_index][1]) # type: ignore
                    row_spans[col_index] = (row_spans[col_index][0]-1, row_spans[col_index][1]) # type: ignore
                    if(row_spans[col_index][0] <= 0): # type: ignore
                        row_spans[col_index] = None
    print(flection_obj)
    return flection_obj


def get_all_text(element: _Element) -> str:
    return ''.join(element.itertext()) # type: ignore

def process_table_header_row(row: _Element):
    num_cols: int = len(find_or_fail(row,'./th'))
    row_spans: list[tuple[int,str]|None] = [None]*num_cols
    
    return num_cols, row_spans

def process_table_header(element: _Element):
    num_cols: int = len(find_or_fail(row,'./th'))
    row_spans: list[tuple[int,str]|None] = [None]*num_cols
    
    return num_cols, row_spans


def get_flection_old(category, es_section):
    flection_obj = None
    flection_table = find(category, xpathqueries['flection'])
    if len(flection_table) > 0:
        
        print("FLECTION TABLE FOUND")
        
        rows = find(flection_table[0], './/tr') # type: ignore
        
        flection_obj = {}
        top_headers = []
        row_spans = []
        num_cols = None
        for row_index, row in enumerate(rows):
            print("Row:", row_index)
            if(num_cols == None):
                num_cols = len(find_or_fail(row,'./th'))
                row_spans = [None]*num_cols
                print("Number of colums:", num_cols)
            
            element: _Element
            
            row_children = row.getchildren()
            row_has_th = False
            for col_index in range(num_cols):
                
                if(col_index < len(row_children)):
                    element: _Element = row_children[col_index]
                    
                    if(element.tag == 'th'):
                        row_has_th = True
                        if(col_index <= len(top_headers)-1):
                            top_headers[col_index] = ''.join(element.itertext())
                        else:
                            top_headers.insert(col_index, ''.join(element.itertext()))
                    if(element.tag == 'td'):
                        
                        if(row_has_th):
                            header = ','.join([top_headers[0], top_headers[col_index]])
                        else:
                            header = ','.join([top_headers[col_index]])
                        
                        row_span = element.get('rowspan')
                        if(row_span != None):
                            row_spans[col_index] = (int(row_span), ''.join(element.itertext())) # type: ignore
                            
                        if(row_spans[col_index] != None):
                            flection_obj[header] = row_spans[col_index][1]
                            print(col_index, header, row_spans[col_index][1]) # type: ignore
                            row_spans[col_index] = (row_spans[col_index][0]-1, row_spans[col_index][1]) # type: ignore
                            if(row_spans[col_index][0] <= 0): # type: ignore
                                row_spans[col_index] = None
                        else:
                            flection_obj[header] =  ''.join(element.itertext())
                            print(col_index, header, ''.join(element.itertext()))
                else:
                    if(row_spans[col_index] != None):
                        
                            if(row_has_th):
                                header = ','.join([top_headers[0], top_headers[col_index]])
                            else:
                                header = ','.join([top_headers[col_index]])
                            
                            flection_obj[header] = row_spans[col_index][1]
                            print(col_index, header, row_spans[col_index][1]) # type: ignore
                            row_spans[col_index] = (row_spans[col_index][0]-1, row_spans[col_index][1]) # type: ignore
                            if(row_spans[col_index][0] <= 0): # type: ignore
                                row_spans[col_index] = None
    print(flection_obj)
    return flection_obj