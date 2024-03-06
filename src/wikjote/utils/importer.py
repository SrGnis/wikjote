import importlib.util
import sys

runtime_modules = {}


def import_module(name: str, is_file: bool = False):
    # code from https://docs.python.org/3/library/importlib.html

    if name in sys.modules:
        runtime_modules[name] = sys.modules[name]
    else:
        if is_file:
            spec = importlib.util.spec_from_file_location(name, name)
        else:
            spec = importlib.util.find_spec(name)

        if spec is not None:
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)  # type: ignore

            runtime_modules[name] = module

            print(f"[INFO    ]: {name!r} has been imported")
        else:
            print(f"[ERROR   ]: can't find the {name!r} module")
            exit(1)


def get_class(module: str, class_name: str) -> type:
    return getattr(runtime_modules[module], class_name)
