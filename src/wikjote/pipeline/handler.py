from __future__ import annotations
import logging

from typing import Any


class Handler:
    _input_type: list[type]
    _output_type: type
    _concurrent: bool
    logger: logging.Logger = logging.getLogger("wikjote")

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def process(self, data: Any) -> Any:
        pass

    @classmethod
    def get_input_type(cls) -> list[type]:
        return cls._input_type

    @classmethod
    def get_output_type(cls) -> type:
        return cls._output_type

    @classmethod
    def is_concurrent(cls) -> bool:
        return cls._concurrent

    @classmethod
    def is_compatible(cls, pre_handler: type[Handler]) -> bool:
        return pre_handler.get_output_type() in cls._input_type
