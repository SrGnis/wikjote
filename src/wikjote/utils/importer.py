"""
Module: WikiJote Import Module Handler

This module provides functionalities to import Python modules 
by name or file path and retrieve classes from imported modules.
It also manages the runtime_modules dictionary for storing loaded modules.

Functions:
- `import_module(name: str, is_file: bool = False)`: Imports a Python module by its 
    given name (or file path) using either filesystem or package search mechanisms.
    Imported modules are stored in `runtime_modules`.
- `get_class(module: str, class_name: str)`: Retrieves a Python class from an imported
    module by its name. It uses the `runtime_modules` dictionary to fetch the specified class.

Usage Example:
To import and use a module's functionality within your code, simply call `import_module()` 
with the appropriate parameters and then retrieve desired classes using `get_class()`. For example:
```python
    import_module("example_module")  # Import an existing module or file path.
    ClassObj = get_class("example_module", "ClassName")  # Retrieve a class from the imported module.
```
"""

import importlib.util
import logging
import sys

logger: logging.Logger = logging.getLogger("wikjote")

runtime_modules = {}


def import_module(name: str, is_file: bool = False):
    """Imports a Python module by name or path.

    This function attempts to load and execute the given module
    from its specified location in the filesystem or as an available
    package on the system. If the module does not exist, an error
    will be logged and the process will exit with status code 1. 
    The imported module is stored in `runtime_modules` for later access.

    Armunoring arguments:
    
        name (str): Name or path of the module to import as a string.
        
        is_file (bool, optional): Specifies whether `name` refers to a file containing the source code for the module. Defaults to False.
    
    Returns:
        None

    Note: 
        Code from https://docs.python.org/3/library/importlib.html
    """

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

            logger.info("Module %s has been imported", name)
        else:
            logger.error("Can't find the %s module", name)
            exit(1)


def get_class(module: str, class_name: str) -> type:
    """Retrieve a Python class from a module by its name."""
        
    return getattr(runtime_modules[module], class_name)
