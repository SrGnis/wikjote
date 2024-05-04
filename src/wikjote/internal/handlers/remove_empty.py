from __future__ import annotations

from wikjote.pipeline.handler import Handler


class RemoveEmptyHandler(Handler):
    _input_type = [list[dict]]
    _output_type = list[dict]
    _concurrent = True

    def process(self, data: list[dict]) -> list[dict]:

        to_remove: list[int] = []
        for index, data_entry in enumerate(data):
            if data_entry.get("sections", []) == []:
                to_remove.append(index)
                self.logger.info("Removed page: %s", data_entry.get("page", None))

        to_remove.reverse()
        for index in to_remove:
            del data[index]

        return data
