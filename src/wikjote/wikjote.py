import os
import argparse
import logging

from extractor import process_zim
import config
from utils import osutils, netutils
from queries import xpathqueries

from rules.assignator import ProcessorAssignator
from rules.namerule import NameRule
from rules.xpathrule import XPathRule

from internal.processors.defaultprocessor import DefaultProcessor
from internal.processors.listprocessor import ListProcessor
from internal.processors.translationsprocessor import TranslationsProcessor
from internal.processors.sensesprocessor import SensesProcessor
from internal.processors.languageprocessor import LanguageProcessor
from internal.processors.tableprocessor import TableProcessor

logger: logging.Logger = logging.getLogger("wikjote")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", type=str, default="/tmp")
    zimgroup = parser.add_mutually_exclusive_group()
    parser.add_argument("-n", "--no_download", action="store_true")
    zimgroup.add_argument("-p", "--zim_path", type=str)
    zimgroup.add_argument("-u", "--zim_url", type=str)

    return parser.parse_args()


def init_config(args):
    config.parent_dir = args.directory

    if config.parent_dir == "/tmp":
        config.working_dir = os.path.join(config.parent_dir, "wikjote")
    else:
        config.working_dir = config.parent_dir

    config.downloads_dir = os.path.join(config.working_dir, "downloads")

    if args.zim_path is None:
        config.zimfile = os.path.join(config.downloads_dir, "wiktionary_es.zim")
    else:
        config.zimfile = args.zim_path

    # TODO do it in a config file
    config.default_processor = DefaultProcessor


def init_folders():
    osutils.mkdir_if_not_exists(config.parent_dir)
    osutils.mkdir_if_not_exists(config.working_dir)
    osutils.mkdir_if_not_exists(config.downloads_dir)


def download_zim(args):
    logger.info("Downloading zim")
    if args.zim_url is None:
        netutils.download_last_zim(config.zimfile)
    else:
        netutils.download_file(args.zim_url, config.zimfile)


def register_rules():
    logger.info("Registring rules")
    ProcessorAssignator.add_rule(NameRule("Etimología", DefaultProcessor, "etymology"))
    ProcessorAssignator.add_rule(NameRule("Locuciones", ListProcessor, "idioms"))
    ProcessorAssignator.add_rule(
        NameRule("Información adicional", ListProcessor, "additional_info")
    )
    ProcessorAssignator.add_rule(NameRule("Véase también", ListProcessor, "see_more"))
    ProcessorAssignator.add_rule(
        NameRule("Traducciones", TranslationsProcessor, "translations")
    )
    ProcessorAssignator.add_rule(
        XPathRule(xpathqueries["language_section_rule"], LanguageProcessor, "languaje")
    )
    ProcessorAssignator.add_rule(NameRule("Forma verbal", SensesProcessor, "verb_form"))
    ProcessorAssignator.add_rule(
        XPathRule(xpathqueries["sense_section_rule"], SensesProcessor, "senses")
    )
    ProcessorAssignator.add_rule(NameRule("Conjugación", TableProcessor, "conjugation"))
    logger.info("%d rules registered", len(ProcessorAssignator.rules))


def init_logger():
    ch = logging.StreamHandler()

    formatter = logging.Formatter("%(levelname)s: %(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)


if __name__ == "__main__":
    init_logger()
    arguments = parse_args()
    register_rules()
    init_config(arguments)

    init_folders()

    if not arguments.no_download and arguments.zim_path is None:
        download_zim(arguments)

    process_zim()
