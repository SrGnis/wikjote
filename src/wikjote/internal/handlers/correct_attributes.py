from __future__ import annotations

import re

from wikjote.pipeline.handler import Handler


class CorrectAttributesHandler(Handler):
    _input_type = [list[dict]]
    _output_type = list[dict]
    _concurrent = True

    def process(self, data: list[dict]) -> list[dict]:

        #TODO: search in all the section tree
        for data_entry in data:
            for section in data_entry.get('sections', []):
                to_remove: list[int] = []
                subsections = section.get('sub_sections', [])
                for subsection in subsections:
                    if subsection.get("type") == "senses":
                        contents = subsection.get("contents",{})
                        senses = contents.get("senses",[])
                        for index, sense in enumerate(senses):
                            if sense.get("title", "") is None and sense.get("content") is not None and sense.get("attributes", {}).get("ejemplos") is "" and index > 0:
                                senses[index-1]["attributes"]["ejemplos"] = sense.get("content")
                                to_remove.append(index)
                                self.logger.info("Removed bad ejemplos: %s", subsection.get('name', None))
                        to_remove.reverse()
                        for index in to_remove:
                            del senses[index]


        return data
