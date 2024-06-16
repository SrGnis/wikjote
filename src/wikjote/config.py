import importlib.resources

import wikjote.utils.osutils as osutils
import wikjote.utils.importer as importer
from wikjote.processors.procesor import Processor


class WikjoteConfig:
    """Configuration class for Wikjote
    
    This class stores various configuration settings and parameters used by the Wikjote application, 
    those setting can be set or overwritten by the input arguments or config file. 
    
    Attributes:
        - command (str): The primary command used for invoking Wikjote.
        - logger_level (str): Logging level to set for the application's logging system.
        - working_dir (str): Path to the working directory where files will be stored.
        - downloads_dir (str): Directory path to store downloaded files or resources.
        - pretty_print (bool): Flag indicating whether pretty print on json output.
        
        - zimfile (str): The ZIM file used by Wikjote for parsing and indexing text data.
        - lemas (list[str] | None): A list of lemma strings to convert from the zim file, if None all will be converted.
        - rules (list[dict]): Custom rule set applied during converting. Each dictionary represents a single rule.
        - nd_output (bool): Flag indicating whether to use Newline Delimited JSON (ndjson) Format.
        
        - process_input (str): JSON file to use as input for the processing.
        - process_output (str): Output destination of processed data.
        - process_workers_num (int): Number of worker threads to utilize during processing.
        - pipeline (list[dict]): List of dictionaries representing a sequence of processing steps in the Wikjote workflow.
        
        - default_processor (type[Processor]): The type of processor used by default; this can be overridden to implement custom processors.
    
    """
        
    command: str
    logger_level: str
    working_dir: str
    downloads_dir: str
    pretty_print: bool

    zimfile: str
    lemas: list[str] | None = None
    rules: list[dict]
    nd_output: bool = False

    process_input: str
    process_output: str
    process_workers_num: int
    pipeline: list[dict]

    default_processor: type[Processor]


def print_default_config():
    """Prints the default configuration to the stdout."""

    file = importlib.resources.open_text("wikjote", "default_config.json")
    print(file.read())


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


def read_config(path: str | None):
    """
    Reads a configuration file from specified path and fills the `WikjoteConfig`.

    This function reads a configuration file located at the given `path`, then sets them as an attribute 
    in a global configuration object, `WikjoteConfig`.
    Specifically focusing on "default_processor". If found, it imports the corresponding 
    module and class dynamically using `wikjote.utils.importer`
    """
    
    json_config: dict = osutils.read_json(path)

    for key, value in json_config.items():
        if key == "default_processor":
            importer.import_module(value["module_name"], value["is_file"])
            WikjoteConfig.default_processor = importer.get_class(
                value["module_name"], value["class_name"]
            )
        else:
            setattr(WikjoteConfig, key, value)
