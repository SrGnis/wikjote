import logging
from typing import Any

from wikjote.htmlobject import HTMLObject


class Processor:
    """Processor class is responsible for processing target_object into a structured data format suitable for JSON conversion.
    
    This abstract base class defines the basic structure and behavior for processors
    that convert HTML objects into JSON-friendly data structures. It requires subclasses 
    to implement the `run` method, which performs this conversion. 
    The Processor can be initialized with an instance of `HTMLObject`.
    
    """
        
    logger: logging.Logger = logging.getLogger("wikjote")

    def __init__(self, target_object: HTMLObject, section_type: None | str = None):
        self.object = target_object
        self.section_type = section_type

    def run(self) -> Any:
        """This method should convert the `target_object` in to a data structure that will be coveted to JSON"""
        return None
