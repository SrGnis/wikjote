from __future__ import annotations

import re

from wikjote.pipeline.handler import Handler


class RemoveSubsectionsHandler(Handler):
    _input_type = [list[dict]]
    _output_type = list[dict]
    _concurrent = True

    def process(self, data: list[dict]) -> list[dict]:
        attr = getattr(self, "attribute")
        pattern = getattr(self, "pattern")

        #TODO: search in all the section tree
        for data_entry in data:
            for section in data_entry.get('sections', []):
                to_remove: list[int] = []
                subsections = section.get('sub_sections', [])
                for index, subsection in enumerate(subsections):
                    if bool(re.search(pattern, subsection.get(attr, ""))):
                        to_remove.append(index)
                        self.logger.info("Removed sub_sections: %s", subsection.get('name', None))
                to_remove.reverse()
                for index in to_remove:
                    del subsections[index]


        return data
