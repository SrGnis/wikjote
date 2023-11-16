from processors.procesor import Processor
from utils import tableparser


class TableProcessor(Processor):
    def run(self):
        return tableparser.parse_table(self.object.root)
