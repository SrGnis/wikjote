import importlib.resources
import pprint

import wikjote.utils.osutils as osutils
import wikjote.utils.importer as importer


class WikjoteConfig:
    parent_dir: str
    working_dir: str
    downloads_dir: str
    zimfile: str
    logger_level: str
    lemas: list[str] | None = None
    rules: list[dict]
    nd_output: bool = False

    default_processor = None


def print_default_config():
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
    json_config: dict = osutils.read_json(path)

    for key, value in json_config.items():
        if key == "default_processor":
            importer.import_module(value["module_name"], value["is_file"])
            WikjoteConfig.default_processor = importer.get_class(
                value["module_name"], value["class_name"]
            )
        else:
            setattr(WikjoteConfig, key, value)

    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(vars(WikjoteConfig))
