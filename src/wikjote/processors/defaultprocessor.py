from typing import Any

from wikjote.processors.procesor import Processor


class DefaultProcessor(Processor):
    def run(self) -> Any:
        return self.object.text()
