from wikjote.processors.procesor import Processor
from wikjote.rules.assignationrule import AssignationRule
import wikjote.config as config


class ProcessorAssignator:
    """
    `ProcessorAssignator` class provides a way to assign processors to sections based on predefined rules. 
    
    It utilizes `AssignationRule` instances to determine which processor should be assigned 
    for different sections in the data. The class maintains a registry of these assignment 
    rules, allowing easy addition and removal. 


    Class Methods:
        - add_rule(rule: AssignationRule) -> None
            Adds a new assignment rule to the registry.
        - assign(section: "Section") -> Processor
            Assigns a processor to a given section by iterating through all defined rules. If no rule matches, it falls back to the default processor specified in the configuration.
        - remove_rule(rule: AssignationRule) -> None
            Removes an existing assignment rule from the registry based on its key (derived from the rule class and type).

    Attributes:
        - `rules`: A dictionary that stores registered assignment rules indexed by their key (combination of class name and type).
    """

    rules: dict[str, AssignationRule] = {}

    default: type[Processor]

    @staticmethod
    def add_rule(rule: AssignationRule):
        """Adds a new assignment rule to the registry."""

        # TODO: check no duplicates
        rule_key = "".join(filter(None, [rule.__class__.__name__, rule.type]))
        ProcessorAssignator.rules[rule_key] = rule

    @staticmethod
    def assign(section: "Section") -> Processor:  # type: ignore
        """
        Assigns a processor to a given section by iterating through all defined rules. 
        
        If no rule matches, it falls back to the default processor specified in the configuration.
        """

        res = config.WikjoteConfig.default_processor(section)  # type: ignore
        for rule in ProcessorAssignator.rules.values():
            if rule.evaluate(section):
                res = rule.processor(section, rule.type)
                break
        return res

    @staticmethod
    def remove_rule(rule: AssignationRule):
        """Removes an existing assignment rule from the registry."""
        
        rule_key = "".join(filter(None, [rule.__class__.__name__, rule.type]))
        del ProcessorAssignator.rules[rule_key]
