from typing import Any
from processors.procesor import Processor
from utils import tableparser


class TableProcessor(Processor):
    def run(self) -> Any:
        res = {}
        try:
            res = tableparser.parse_table(self.object.root)
        except Exception:
            self.logger.error('Error getting table in "%s"', self.object.stack_string())
        return res
