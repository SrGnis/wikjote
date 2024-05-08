import logging
from typing import Any

from wikjote.pipeline.handler import Handler
from wikjote.pipeline.pipelineworker import PipelineWorker


class Pipeline:
    """
    Note: Well I just learned about GIL... so basicaly parallelism is not posible right now,
    so until furter notice just use one worker
    """

    def __init__(self, data: Any, num_workers: int):
        self._input: Any = data
        self._workers: list[PipelineWorker] = [
            PipelineWorker() for x in range(num_workers)
        ]
        self.workers_step: dict[PipelineWorker, int] = {
            self._workers[i]: -1 for i in range(len(self._workers))
        }

        self._output: Any = None
        self._handlers: list[type[Handler]] = []
        self._handlers_args: list[dict[str, Any]] = []
        self._running: bool = False

        self.logger: logging.Logger = logging.getLogger("wikjote")

    def add_handler(self, handler: type[Handler], arguments: dict[str, Any]):
        if len(self._handlers) == 0 or handler.is_compatible(self._handlers[-1]):
            self._handlers.append(handler)
            self._handlers_args.append(arguments)
        else:
            raise IncompatibleHandlersError(self._handlers[-1], handler)

    def start(self):

        splited_data = self._split_data()

        # distribute the data
        for index, worker in enumerate(self._workers):
            worker.set_data(splited_data[index])

        runnig_workers = self._workers.copy()
        while len(runnig_workers) > 0:
            for worker in self._workers:
                if worker in runnig_workers and not worker.is_runnig():
                    step = self.workers_step[worker]
                    next_step = step + 1

                    if next_step == len(self._handlers):
                        runnig_workers.remove(worker)
                        continue

                    next_handler = self._handlers[next_step]

                    if next_handler.is_concurrent():
                        worker.join()
                        self.workers_step[worker] = next_step
                        worker.set_handler(
                            self._handlers[next_step](**self._handlers_args[next_step])
                        )
                        worker.start()
                    else:
                        self._switch_no_concurrent(next_step)

        # all the workers are done merge the data
        self._output = self._merge_data()

    def _switch_no_concurrent(self, concurrent_index):

        # wait until all the workers arrive to the no concurrent handler
        tmp_workers = self._workers.copy()
        while len(tmp_workers) > 0:
            for worker in self._workers:
                if worker in tmp_workers and not worker.is_runnig():
                    worker.join()
                    step = self.workers_step[worker]
                    next_step = step + 1
                    if next_step == concurrent_index:
                        tmp_workers.remove(worker)
                    else:
                        self.workers_step[worker] = next_step
                        worker.set_handler(
                            self._handlers[next_step](**self._handlers_args[next_step])
                        )
                        worker.start()

        # merge the data of all workers
        data_merged = self._merge_data()
        # setup a worker with the no concurrent handler
        concurrent_worker = self._workers[0]
        self.workers_step[concurrent_worker] = concurrent_index
        concurrent_worker.set_handler(
            self._handlers[concurrent_index](**self._handlers_args[concurrent_index])
        )
        concurrent_worker.set_data(data_merged)
        # start the worker and wait for him to finish
        concurrent_worker.start()
        concurrent_worker.join()
        # split and distribute the data
        splited_data = self._split_data(concurrent_worker.get_data())
        for index, worker in enumerate(self._workers):
            worker.set_data(splited_data[index])
        # advance the remainig workers
        for worker in self._workers[1:]:
            self.workers_step[worker] = concurrent_index
        # return to concurrent operation

    def _split_data(self, data: Any = None) -> list[Any]:
        if data is None:
            data_to_split = self._input
        else:
            data_to_split = data

        # TODO: add more ways to split data
        return list(self._split(data_to_split, len(self._workers)))

    @staticmethod
    def _split(lst: list, n: int):
        # from https://stackoverflow.com/a/2135920/12014643
        k, m = divmod(len(lst), n)
        for i in range(n):
            yield lst[i * k + min(i, m) : (i + 1) * k + min(i + 1, m)]

    def _merge_data(self) -> Any:
        # TODO: add more ways to merge data
        merged_data = []
        for worker in self._workers:
            merged_data += worker.get_data()
        return merged_data

    def is_runnig(self) -> bool:
        return self._running

    def get_output(self):
        if not self.is_runnig():
            return self._output
        # else throw exeption?


class IncompatibleHandlersError(BaseException):
    def __init__(self, pre_handler: type[Handler], new_handler: type[Handler]):
        self.pre_handler = pre_handler
        self.new_handler = new_handler
        super().__init__(
            f"Tried to append Handlers with incompatible I/O types. \
            {self.new_handler.__name__} with input types: {self.new_handler.get_input_type()}, \
            tried to be appended to {self.pre_handler.__name__} with output type: {self.pre_handler.get_output_type()}"
        )
