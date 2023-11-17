from processors.defaultprocessor import DefaultProcessor
from processors.procesor import Processor

parent_dir: str
working_dir: str
downloads_dir: str
zimfile: str
default_processor: type[Processor] = DefaultProcessor
