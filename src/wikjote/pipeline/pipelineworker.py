from typing import Any

from threading import Thread

from wikjote.pipeline.handler import Handler


class PipelineWorker:
    """
    A worker class for handling data processing within a pipeline. It allows 
    executing handlers on input data.
    
    Attributes:
        _data (Any): The current data to be processed.
        _current_handler (Handler): The currently active handler being executed.
    
    Methods:
        start(): Starts the worker thread for processing data.
        join(): Waits until the handler completes and joins the thread.
        run(): Executes the current handler's process method on the provided data.
        is_runnig(): Checks if the worker instance is currently running a task.
        set_data(data): Sets the input data for processing by updating the internal state of the object.
        get_data(): Retrieves the processed output data from the worker's internal state.
        set_handler(handler): Updates the current handler.
    """

    def __init__(self):
        self._data: Any
        self._current_handler: Handler
        self._thread: Thread | None = None

    def start(self):
        """Starts the worker's processing task by initiating a new thread."""

        self._thread = Thread(target=self.run)
        self._thread.start()

    def join(self):
        """ Waits until the handler completes and joins the thread."""

        if self._thread is not None:
            self._thread.join()

    def run(self):
        """Executes the current handler's process method on the provided data."""

        self._data = self._current_handler.process(self._data)

    def is_runnig(self) -> bool:
        """Checks if the worker instance is currently running a handler"""

        return False if self._thread is None else self._thread.is_alive()

    def set_data(self, data: Any):
        """Sets the input data for processing by updating the internal state of the object."""

        if not self.is_runnig():
            self._data = data
        # else throw exception?

    def get_data(self) -> Any:
        """Retrieves the processed output data from the worker's internal state."""

        return self._data

    def set_handler(self, handler: Handler):
        """Updates the current handler."""

        if not self.is_runnig():
            self._current_handler = handler
        # else throw exception?
