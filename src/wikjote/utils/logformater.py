import logging, inspect


class IndentFormatter(logging.Formatter):
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
