from __future__ import annotations

from wikjote.pipeline.handler import Handler


class FilterHandler(Handler):
    _input_type = [list[dict]]
    _output_type = list[dict]
    _concurrent = True

    def process(self, data: list[dict]) -> list[dict]:
        # target: list[str | dict[str, str]] = getattr(self, "target")

        target = ["sections", {"name": "Español"}]

        for data_entry in data:
            data_step = data_entry
            for target_step in target:
                if isinstance(target_step, str):
                    data_step = data_step.get(target_step)  # type: ignore
                    if data_step is None:
                        # FIXME use a remove list
                        data.remove(data_entry)
                        self.logger.info("Removed")
                        break
                else:
                    to_remove = []
                    for section in data_step:
                        for key, value in target_step.items():
                            section_value = section.get(key)  # type: ignore
                            if section_value is None or section_value != value:
                                to_remove.append(section)
                                break
                            else:
                                self.logger.info(
                                    "Keep %s %s",
                                    data_entry["page"],
                                    section["name"],
                                )

                    for item in to_remove:
                        data_step.remove(item)  # type: ignore
                        self.logger.info(
                            "Removed %s %s",
                            data_entry["page"],
                            item["name"],
                        )
        return data
