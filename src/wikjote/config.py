from processors.defaultprocessor import DefaultProcessor
from processors.procesor import Processor
import utils.osutils as osutils

parent_dir: str
working_dir: str
downloads_dir: str
zimfile: str
default_processor: type[Processor] = DefaultProcessor
logger_level: str
lemas: list[str]


def load_lemas_file(path):
    try:
        read_lemas = osutils.read_json(path)
        if isinstance(read_lemas, list):
            return read_lemas
        else:
            print("ERROR: The lemas json should be a list")
            exit(1)
    except Exception:
        read_lemas = osutils.read_list(path)
        return read_lemas
