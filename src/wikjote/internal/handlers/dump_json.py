from __future__ import annotations

from wikjote.pipeline.handler import Handler
from wikjote.utils import osutils


class DumpJsonHandler(Handler):
    _input_type = [list[dict]]
    _output_type = list[dict]
    _concurrent = False

    def process(self, data: list[dict]) -> list[dict]:
        output_path = getattr(self, "output_path")

        self.logger.info("Dumping data into %s", output_path)

        osutils.write_json(output_path, data)

        self.logger.info("Done dumping")

        return data
