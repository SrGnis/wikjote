from htmlobject import HTMLObject
from processors.procesor import Processor
from processors.defaultprocessor import DefaultProcessor

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