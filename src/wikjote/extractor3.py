import json
import os
import config
from lxml import etree
from lxml.etree import _Element
from libzim.reader import Archive 
from page import Page
import traceback

def process_zim2():
    print("Processing zim")
    
    zim = Archive(config.zimfile)
    
    # titles = [entry.title for entry in zim] not implemented yet
    # titles = [zim._get_entry_by_id(id).title for id in range(zim.all_entry_count)]
    
    # print(json.dumps(titles, ensure_ascii=False, indent= 2)) #debug
    
    with open(os.path.join(config.downloads_dir, 'eswiktionary-titles'), encoding='utf8') as f:
        f = ['flor']
        for lema in f:
            try:
                lema = lema.strip()
                entry = zim.get_entry_by_path(lema)
                entry_content = bytes(entry.get_item().content).decode("UTF-8")
                entry_html: _Element = etree.HTML(entry_content) # type: ignore
                
                page = Page(entry_html, lema)
                
                # print('Page:', page.lema, 'Languajes:', page.sections) #debug

                page.process()
                
            except Exception as e: 
                print('Error in lema: ', lema)
                traceback.print_exc()
                
def save_page(page_html: str, lema: str):
    with open(os.path.join(config.working_dir, lema+'.html'), 'w') as file:
        file.write(page_html)
        
