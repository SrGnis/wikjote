# REALY INEFFICIENT DO NOT USE
#
#from __future__ import annotations
#from typing import Callable, Any
#
#import re
#
#from jsonpath_ng import jsonpath, parse
#
#from wikjote.pipeline.handler import Handler
#
#class FilterHandler(Handler):
#    _input_type = [list[dict]]
#    _output_type = list[dict]
#    _concurrent = True
#
#    _false = lambda self, x=None, y=None : False
#    _empty = lambda self, x, y=None : (not x)
#    _equals = lambda self, x, y : x == y
#    _notequals = lambda self, x, y : x != y
#    _regex = lambda self, value, pattern : bool(re.search(pattern, value))
#
#    def process(self, data: list[dict]) -> list[dict]:
#        # target: list[str | dict[str, str]] = getattr(self, "target")
#
#        rules= [
#            {
#                "name": "only_spanish",
#                "path": "[*].sections[*].name",
#                "condition": {
#                    "function": "notequals",
#                    "argument": "Español"
#                },
#                "trim_level": 3
#            },
#            {
#                "name": "remove_empty",
#                "path": "[*].sections",
#                "condition":{
#                    "function": "empty"
#                },
#                "trim_level": 1
#            },
#            {
#                "name": "remove_forms",
#                "path": "[*].sections[*].sub_sections[*].name",
#                "condition": {
#                    "function": "regex",
#                    "argument": "Forma.*"
#                },
#                "trim_level": 4
#            },
#        ]
#
#        for rule in rules:
#            rule_path: str = rule['path']
#
#            rule_name: dict[str,str] = rule['name']
#            rule_condition: dict[str,str] = rule['condition']
#            rule_fn_str: str = rule_condition.get("function","false")
#            rule_fn: Callable[[Any, Any], bool] = getattr(self, '_'+rule_fn_str)
#            rule_arg = rule_condition.get("argument", None)
#            rule_trim_level = rule_condition.get("trim_leve", -1)
#
#            self.logger.info("Applying filter %s", rule_name)
#
#            jsonpath_expr = parse(rule_path)
#
#            found = jsonpath_expr.find(data)
#
#            # get all the paths
#            paths = [str(match.full_path) for match in found]
#
#            # get wich of those paths fulfill the condition
#            matches = [rule_fn(match.value, rule_arg) for match in found]
#
#            # filter the paths with the ones that are true
#            matched_paths = [item for item, value in zip(paths, matches) if value]
#
#            # trim the paths with the level seted in the rule
#            trimed_paths = [trim_path(item, rule_trim_level) for item in matched_paths] # type: ignore
#
#            # remove duplicates
#            trimed_paths = list( dict.fromkeys(trimed_paths) )
#
#            for path in trimed_paths:
#                jsonpath_expr = parse(path)
#                jsonpath_expr.filter(lambda d: True, data)
#
#            self.logger.info("Filter %s removed %d elements.", rule_name, len(trimed_paths))
#
#        return data
#
#def trim_path(path: str, trim_level: int) -> str:
#    path_list = path.split('.')
#    return '.'.join(path_list[:trim_level])
#

