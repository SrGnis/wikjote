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
    
    with open(os.path.join(config.downloads_dir, 'eswiktionary-titles'), encoding='utf8') as f:
        f = ['flor']
        for lema in f:
            try:
                lema = lema.strip()
                entry = zim.get_entry_by_path(lema)
                entry_content = bytes(entry.get_item().content).decode("UTF-8")
                entry_html: _Element = etree.HTML(entry_content) # type: ignore
                
                page = Page(entry_html, lema)
                
                print('Page:', page.lema, 'Languajes:', page.languajes) #debug
                
            except Exception as e: 
                print('Error in lema: ', lema)
                traceback.print_exc()