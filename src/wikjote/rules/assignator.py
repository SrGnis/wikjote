from wikjote.processors.procesor import Processor
from wikjote.rules.assignationrule import AssignationRule
import wikjote.config as config


class ProcessorAssignator:
    rules: dict[str, AssignationRule] = {}

    default: type[Processor] = config.WikjoteConfig.default_processor

    @staticmethod
    def add_rule(rule: AssignationRule):
        # TODO: check no duplicates
        rule_key = "".join(filter(None, [rule.__class__.__name__, rule.type]))
        ProcessorAssignator.rules[rule_key] = rule

    @staticmethod
    def assign(section: "Section") -> Processor:  # type: ignore
        res = config.WikjoteConfig.default_processor(section)  # type: ignore
        for rule in ProcessorAssignator.rules.values():
            if rule.evaluate(section):
                res = rule.processor(section, rule.type)
                break
        return res

    @staticmethod
    def remove_rule(rule: AssignationRule):
        rule_key = "".join(filter(None, [rule.__class__.__name__, rule.type]))
        del ProcessorAssignator.rules[rule_key]
