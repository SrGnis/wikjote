from extractor3 import process_zim2
import config
import os
import argparse
from utils import osutils, netutils
from registry import ProcessorRegistry

from processors.defaultprocessor import DefaultProcessor
from processors.listprocessor import ListProcessor
from processors.translationsprocessor import TranslationsProcessor
from processors.sensesprocessor import SensesProcessor
from processors.tableprocessor import TableProcessor
from processors.languageprocessor import LanguageProcessor
from processors.attributeprocessor import AttributeProcessor


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, default='/tmp')
    zimgroup = parser.add_mutually_exclusive_group()
    parser.add_argument('-n', '--no_download', action="store_true")
    zimgroup.add_argument('-p', '--zim_path', type=str)
    zimgroup.add_argument('-u', '--zim_url', type=str)
    
    args = parser.parse_args()
    
    return args

def init_config(args):
    config.parent_dir = args.directory
    
    if(config.parent_dir == '/tmp'):
        config.working_dir = os.path.join(config.parent_dir, 'wikjote')
    else:
        config.working_dir = config.parent_dir
        
    config.downloads_dir = os.path.join(config.working_dir,'downloads')
    
    if(args.zim_path == None):
        config.zimfile = os.path.join(config.downloads_dir, 'wiktionary_es.zim')
    else:
        config.zimfile = args.zim_path

def init_folders():
    osutils.mkdir_if_not_exists(config.parent_dir)
    osutils.mkdir_if_not_exists(config.working_dir)
    osutils.mkdir_if_not_exists(config.downloads_dir)
    
    
def download_zim():
    if( args.zim_url == None):
        netutils.download_last_zim(config.zimfile)
    else:
        netutils.download_file(args.zim_url, config.zimfile)
        
def register_processors():
    
    ProcessorRegistry.register('Etimología', DefaultProcessor)
    ProcessorRegistry.register('Locuciones', ListProcessor)
    ProcessorRegistry.register('Información adicional', ListProcessor)
    ProcessorRegistry.register('Véase también', ListProcessor)
    ProcessorRegistry.register('Traducciones', TranslationsProcessor)
    ProcessorRegistry.register('Senses', SensesProcessor)
    ProcessorRegistry.register('Table', TableProcessor)
    ProcessorRegistry.register('Language', LanguageProcessor)

if __name__ == "__main__":
    args = parse_args()
    register_processors()
    init_config(args)
    
    init_folders()
    
    if(not args.no_download and args.zim_path == None):
        download_zim()
        
    process_zim2()