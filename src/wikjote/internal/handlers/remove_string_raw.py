from __future__ import annotations

import json
import re

from wikjote.pipeline.handler import Handler


class ReplaceStringRawHandler(Handler):
    _input_type = [list[dict]]
    _output_type = list[dict]
    _concurrent = True

    def process(self, data: list[dict]) -> list[dict]:
        replacement: str = getattr(self, "replacement")
        pattern_str: str | None = getattr(self, "pattern_str", None)
        pattern_regex: str | None = getattr(self, "pattern_regex", None)

        
        if(pattern_regex is not None):
            pattern = pattern_regex
        elif(pattern_str is not None):
            pattern = re.escape(pattern_str)
        else:
            self.logger.warning('No pattern found to replace')
            return data

        raw_json = json.dumps(data, ensure_ascii=False)

        raw_json = re.sub(pattern, replacement, raw_json)

        return json.loads(raw_json)
