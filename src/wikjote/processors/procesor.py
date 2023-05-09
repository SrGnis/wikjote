from htmlobject import HTMLObject
from abc import abstractmethod, ABCMeta

class Processor(ABCMeta):

    def __init__(self, object: HTMLObject):
        self.object = object

    @abstractmethod
    def run(self) -> None:
        pass