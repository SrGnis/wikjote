from typing import Any

from threading import Thread

from wikjote.pipeline.handler import Handler


class PipelineWorker:
    def __init__(self):
        self._data: Any
        self._current_handler: type[Handler]
        self._thread: Thread | None = None

    def start(self):
        self._thread = Thread(target=self.run())
        self._thread.start()

    def join(self):
        if self._thread is not None:
            self._thread.join()

    def run(self):
        self._data = self._current_handler.process(self._data)

    def is_runnig(self) -> bool:
        return False if self._thread is None else self._thread.is_alive()

    def set_data(self, data: Any):
        if not self.is_runnig():
            self._data = data
        # else throw exeption?

    def get_data(self) -> Any:
        return self._data

    def set_handler(self, handler: type[Handler]):
        if not self.is_runnig():
            self._current_handler = handler
        # else throw exeption?
