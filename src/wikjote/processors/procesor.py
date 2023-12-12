import logging
from typing import Any

from wikjote.htmlobject import HTMLObject


class Processor:
    logger: logging.Logger = logging.getLogger("wikjote")

    def __init__(self, target_object: HTMLObject, section_type: None | str = None):
        self.object = target_object
        self.section_type = section_type

    def run(self) -> Any:
        return None
