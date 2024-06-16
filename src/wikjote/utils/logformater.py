import logging, inspect


class IndentFormatter(logging.Formatter):
    """
    A custom formatter class that enhances readability by adding indentation based on the call stack depth.

    This subclass of `logging.Formatter` provides functionality to indent log records, 
    making it easier to trace their origin within nested function calls or method invocations. 
    The indentation is relative to a baseline, defined as the current position in the 
    call stack when an instance of this formatter is initialized.
    """
    
    def __init__(self, fmt=None, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.baseline = len(inspect.stack())

    def format(self, rec):
        stack = inspect.stack()
        rec.indent = "│ " * (len(stack) - self.baseline - 7)
        rec.function = stack[8][3]
        out = logging.Formatter.format(self, rec)
        del rec.indent
        del rec.function
        return out
