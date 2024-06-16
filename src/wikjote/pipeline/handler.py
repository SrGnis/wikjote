from __future__ import annotations
import logging

from typing import Any


class Handler:
    """
    A class that transform or enrich data executing the `process` method.

    Is intended to be subclassed by overwriting the process method.  

    Attributes:

    - _input_type (list[type]): A list that defines acceptable input types for this Handler class.
    - _output_type (type): The type returned by processing data through this Handler.
    - _concurrent (bool): Indicates whether the handler should process tasks in a concurrent manner or not.
    - logger (logging.Logger): An instance of logging to log messages related to handling operations.

    Methods:
    
    - get_input_type() -> list[type]: Retrieves the list of input types that this Handler class is designed to process.
    - get_output_type() -> type: Returns the output type expected after data has been processed through this handler.
    - is_concurrent() -> bool: Checks whether the processing within this Handler instance should be executed concurrently or sequentially.
    - is_compatible(pre_handler: type[Handler]) -> bool: Returns a bool specifying if the provided handler output type is compatible with this Handler input type.

    """
        
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
        """Retrieves the list of input types that this Handler class is designed to process."""

        return cls._input_type

    @classmethod
    def get_output_type(cls) -> type:
        """Returns the output type expected after data has been processed through this handler."""

        return cls._output_type

    @classmethod
    def is_concurrent(cls) -> bool:
        """Checks whether the processing within this Handler instance should be executed concurrently or sequentially."""

        return cls._concurrent

    @classmethod
    def is_compatible(cls, pre_handler: type[Handler]) -> bool:
        """Returns a bool specifying if the provided handler output type is compatible with this Handler input type."""

        return pre_handler.get_output_type() in cls._input_type
