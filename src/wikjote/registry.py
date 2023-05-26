from htmlobject import HTMLObject
from processors.procesor import Processor
from processors.defaultprocessor import DefaultProcessor
from sections.section import Section

from utils.data import is_sense


class ProcessorRegistry:

    registry: dict[str, type] = {}

    default: type = DefaultProcessor

    @staticmethod
    def register(key: str, object: type):
        #TODO: check no duplicates
        ProcessorRegistry.registry[key] = object
    
    # TODO: is_sense alternative
    @staticmethod
    def get(key: str, root: HTMLObject) -> Processor:
        print(key, '->' ,is_sense(key))
        res = ProcessorRegistry.registry.get(is_sense(key), ProcessorRegistry.default)
        return res(root)
    
    @staticmethod
    def remove( key: str):
        del ProcessorRegistry.registry[key]

class SectionRegistry:

    registry: dict[str, type] = {}

    default: type = Section

    @staticmethod
    def register(key: str, object: type):
        #TODO: check no duplicates
        SectionRegistry.registry[key] = object
    
    # TODO: is_sense alternative
    # TODO: key argument
    @staticmethod
    def get(root: HTMLObject) -> Section:
        key = root.get_section_name()
        print(key, '->' ,is_sense(key)) #debug
        res = SectionRegistry.registry.get(is_sense(key), SectionRegistry.default)
        return res(root.root)
    
    @staticmethod
    def remove( key: str):
        del SectionRegistry.registry[key]