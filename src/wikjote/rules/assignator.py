from processors.procesor import Processor
from processors.defaultprocessor import DefaultProcessor
from rules.assignationrule import AssignationRule


class ProcessorAssignator:
    rules: dict[type, AssignationRule] = {}

    default: Processor = DefaultProcessor

    @staticmethod
    def add_rule(rule: AssignationRule):
        # TODO: check no duplicates
        ProcessorAssignator.rules[rule.__class__.__name__ + rule.type] = rule

    @staticmethod
    def assign(section: "Section") -> Processor:
        res = ProcessorAssignator.default(section)
        for rule in ProcessorAssignator.rules.values():
            if rule.evaluate(section):
                res = rule.processor(section, rule.type)
                break
        return res

    @staticmethod
    def remove_rule(rule: AssignationRule):
        del ProcessorAssignator.rules[rule.__class__]
