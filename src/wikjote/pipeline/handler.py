from __future__ import annotations

from typing import Any, Type


class Handler:
    _input_type: list[type]
    _output_type: type
    _concurrent: bool

    @staticmethod
    def process(data: Any) -> Any:
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
