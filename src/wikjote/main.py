import os
import argparse
import logging

from wikjote.extractor import process_zim
import wikjote.config as config
from wikjote.utils import osutils, netutils
from wikjote.utils.logformater import IndentFormatter
import wikjote.utils.importer as importer

from wikjote.rules.assignator import ProcessorAssignator
from wikjote.rules.namerule import NameRule
from wikjote.rules.xpathrule import XPathRule

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
        "-c", "--config", type=str, help="Specivy the path to the config file"
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
    config.WikjoteConfig.parent_dir = args.directory
    if config.WikjoteConfig.parent_dir == "/tmp":
        config.WikjoteConfig.working_dir = os.path.join(
            config.WikjoteConfig.parent_dir, "wikjote"
        )
    else:
        config.WikjoteConfig.working_dir = config.WikjoteConfig.parent_dir
    config.WikjoteConfig.downloads_dir = os.path.join(
        config.WikjoteConfig.working_dir, "downloads"
    )

    # TODO search zim with different names
    if args.zim_path is None:
        config.WikjoteConfig.zimfile = os.path.join(
            config.WikjoteConfig.downloads_dir, "wiktionary_es.zim"
        )
    else:
        config.WikjoteConfig.zimfile = args.zim_path

    config.WikjoteConfig.logger_level = args.verbose

    config.WikjoteConfig.lemas = args.lemas
    if args.lemas_file is not None:
        config.WikjoteConfig.lemas = config.load_lemas_file(args.lemas_file)

    if args.config is not None:
        config.read_config(args.config)


def init_folders():
    osutils.mkdir_if_not_exists(config.WikjoteConfig.parent_dir)
    osutils.mkdir_if_not_exists(config.WikjoteConfig.working_dir)
    osutils.mkdir_if_not_exists(config.WikjoteConfig.downloads_dir)


def download_zim(args):
    logger.info("Downloading zim ...")
    if args.zim_url is None:
        netutils.download_last_zim(config.WikjoteConfig.zimfile)
    else:
        netutils.download_file(args.zim_url, config.WikjoteConfig.zimfile)


def register_rules():
    logger.info("Registring rules ...")

    for rule_conf in config.WikjoteConfig.rules:
        match rule_conf["type"]:
            case "NameRule":
                rule_class = NameRule
            case "XPathRule":
                rule_class = XPathRule
            case _:
                continue

        processor_conf = rule_conf["processor"]
        importer.import_module(processor_conf["module_name"], processor_conf["is_file"])
        processor = importer.get_class(
            processor_conf["module_name"], processor_conf["class_name"]
        )

        rule = rule_class(rule_conf["args"][0], processor, rule_conf["section_type"])

        ProcessorAssignator.add_rule(rule)

    logger.info("%d rules registered", len(ProcessorAssignator.rules))


def init_logger():
    logger.setLevel(config.WikjoteConfig.logger_level)

    log_handler = logging.StreamHandler()
    if logger.level == logging.DEBUG:
        formatter = IndentFormatter("[%(levelname)-8s]:%(indent)s%(message)s")
    else:
        formatter = logging.Formatter("[%(levelname)-8s]: %(message)s")
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)


def main():
    arguments = parse_args()
    init_config(arguments)
    init_logger()

    init_folders()

    register_rules()

    if not arguments.no_download and arguments.zim_path is None:
        download_zim(arguments)

    process_zim()
    logger.info("DONE")


if __name__ == "__main__":
    main()
