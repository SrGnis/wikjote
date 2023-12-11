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
from utils.logformater import IndentFormatter

logger: logging.Logger = logging.getLogger("wikjote")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default="/tmp",
        help="Directory where the downloads and result files will be created",
    )
    parser.add_argument(
        "-n",
        "--no_download",
        action="store_true",
        help="Do not download the zim. If no 'zim_path' is provided it will search the zim in <directory>/downloads/wiktionary_es.zim",
    )

    zimgroup = parser.add_mutually_exclusive_group()
    zimgroup.add_argument(
        "-p", "--zim_path", type=str, help="Specify the path to the zim file"
    )
    zimgroup.add_argument(
        "-u", "--zim_url", type=str, help="Specify the url to download the file"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        type=str,
        choices=[
            "CRITICAL",
            "FATAL",
            "ERROR",
            "WARN",
            "WARNING",
            "INFO",
            "DEBUG",
            "NOTSET",
        ],
        default="INFO",
        help="Set the log level",
    )

    lemas_group = parser.add_mutually_exclusive_group()
    lemas_group.add_argument("-l", "--lemas", type=str, nargs="+", required=False)
    lemas_group.add_argument("-lf", "--lemas_file", type=str, required=False)

    return parser.parse_args()


def init_config(args):
    config.parent_dir = args.directory
    if config.parent_dir == "/tmp":
        config.working_dir = os.path.join(config.parent_dir, "wikjote")
    else:
        config.working_dir = config.parent_dir
    config.downloads_dir = os.path.join(config.working_dir, "downloads")

    # TODO search zim with different names
    if args.zim_path is None:
        config.zimfile = os.path.join(config.downloads_dir, "wiktionary_es.zim")
    else:
        config.zimfile = args.zim_path

    config.logger_level = args.verbose

    config.lemas = args.lemas
    if args.lemas_file is not None:
        config.lemas = config.load_lemas_file(args.lemas_file)

    # TODO do it in a config file
    config.default_processor = DefaultProcessor


def init_folders():
    osutils.mkdir_if_not_exists(config.parent_dir)
    osutils.mkdir_if_not_exists(config.working_dir)
    osutils.mkdir_if_not_exists(config.downloads_dir)


def download_zim(args):
    logger.info("Downloading zim ...")
    if args.zim_url is None:
        netutils.download_last_zim(config.zimfile)
    else:
        netutils.download_file(args.zim_url, config.zimfile)


def register_rules():
    logger.info("Registring rules ...")
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
    logger.setLevel(config.logger_level)

    log_handler = logging.StreamHandler()
    if logger.level == logging.DEBUG:
        formatter = IndentFormatter("[%(levelname)-8s]:%(indent)s%(message)s")
    else:
        formatter = logging.Formatter("[%(levelname)-8s]: %(message)s")
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)


if __name__ == "__main__":
    arguments = parse_args()
    init_config(arguments)
    init_logger()

    init_folders()

    register_rules()

    if not arguments.no_download and arguments.zim_path is None:
        download_zim(arguments)

    process_zim()
    logger.info("DONE")
