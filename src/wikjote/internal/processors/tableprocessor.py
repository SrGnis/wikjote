from typing import Any
from processors.procesor import Processor
from utils import tableparser


class TableProcessor(Processor):
    def run(self) -> Any:
        return tableparser.parse_table(self.object.root)
