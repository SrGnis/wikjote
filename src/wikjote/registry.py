from wikjote.htmlobject import HTMLObject
from wikjote.processors.procesor import Processor
from wikjote.processors.defaultprocessor import DefaultProcessor

class ProcessorRegistry:

    registry: dict[str, type] = {}

    default: type = DefaultProcessor

    @staticmethod
    def register(key: str, object: type):
        #TODO: check no duplicates
        ProcessorRegistry.registry[key] = object
    
    @staticmethod
    def get(key: str, root: HTMLObject) -> Processor:
        res = ProcessorRegistry.registry.get(key, ProcessorRegistry.default)
        return res(root)
    
    @staticmethod
    def remove( key: str):
        del ProcessorRegistry.registry[key]

# def register_processors():
#     #TODO
#     ProcessorRegistry.register('', DefaultProcessor)
