import os
import argparse
import logging
import pprint

from wikjote.extractor import process_zim
import wikjote.config as config
from wikjote.internal.handlers.structurize_es import StructurizeHandler
from wikjote.pipeline.pipeline import Pipeline
from wikjote.utils import osutils, netutils
from wikjote.utils.logformater import IndentFormatter
import wikjote.utils.importer as importer

from wikjote.rules.assignator import ProcessorAssignator
from wikjote.rules.namerule import NameRule
from wikjote.rules.xpathrule import XPathRule

logger: logging.Logger = logging.getLogger("wikjote")


def parse_args():
    parser = argparse.ArgumentParser()
    # main arguments
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

    parser.add_argument(
        "-c", "--config", type=str, help="Specify the path to the config file"
    )

    parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default="./wikjote_dir",
        help="Directory where the downloads and result files will be created",
    )

    # sub commands
    subparsers = parser.add_subparsers(
        title="subcommands", description="valid subcommands", dest="command"
    )

    # convert command
    convert_parser = subparsers.add_parser(
        "convert", help="Convert a html source into json"
    )

    convert_parser.add_argument(
        "-n",
        "--no_download",
        action="store_true",
        help="Do not download the zim. If no 'zim_path' is provided it will search the zim in <directory>/downloads/wiktionary_es.zim",
    )

    zimgroup = convert_parser.add_mutually_exclusive_group()
    zimgroup.add_argument(
        "-p", "--zim_path", type=str, help="Specify the path to the zim file"
    )
    zimgroup.add_argument(
        "-u", "--zim_url", type=str, help="Specify the url to download the file"
    )

    convert_parser.add_argument(
        "--nd_output",
        action="store_true",
        help="Use new line delimited (NDJSON) as output format",
    )

    lemas_group = convert_parser.add_mutually_exclusive_group()
    lemas_group.add_argument("-l", "--lemas", type=str, nargs="+", required=False)
    lemas_group.add_argument("-lf", "--lemas_file", type=str, required=False)

    # process command
    process_parser = subparsers.add_parser(
        "process", help="Process json data into other json data"
    )

    process_parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Path to the input JSON file",
    )

    process_parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Path to the output JSON file, defaults to <wikjote_dir>/process_output.json",
    )

    process_parser.add_argument(
        "-w",
        "--workers",
        type=int,
        default=1,
        help="Number of workers of the processing pipeline.",
    )

    return parser.parse_args()


def init_config(args):
    """Set up the config of the application using the provided args"""

    config.read_config(args.config)

    config.WikjoteConfig.command = args.command

    config.WikjoteConfig.logger_level = args.verbose

    config.WikjoteConfig.working_dir = args.directory
    config.WikjoteConfig.downloads_dir = os.path.join(
        config.WikjoteConfig.working_dir, "downloads"
    )

    # convert config
    if args.command == "convert":

        config.WikjoteConfig.nd_output = args.nd_output

        # TODO search zim with different names
        if args.zim_path is None:
            config.WikjoteConfig.zimfile = os.path.join(
                config.WikjoteConfig.downloads_dir, "wiktionary_es.zim"
            )
        else:
            config.WikjoteConfig.zimfile = args.zim_path

        if args.lemas is not None:
            config.WikjoteConfig.lemas = args.lemas
        if args.lemas_file is not None:
            config.WikjoteConfig.lemas = config.load_lemas_file(args.lemas_file)

    # process config
    if args.command == "process":

        config.WikjoteConfig.process_input = args.input

        if args.output is None:
            config.WikjoteConfig.process_output = os.path.join(
                config.WikjoteConfig.working_dir, "process_output.json"
            )
        else:
            config.WikjoteConfig.process_output = args.output

        config.WikjoteConfig.process_workers_num = args.workers


def init_folders():
    osutils.mkdir_if_not_exists(config.WikjoteConfig.working_dir)
    osutils.mkdir_if_not_exists(config.WikjoteConfig.downloads_dir)


def download_zim(args):
    logger.info("Downloading zim ...")
    if args.zim_url is None:
        netutils.download_last_zim(config.WikjoteConfig.zimfile)
    else:
        netutils.download_file(args.zim_url, config.WikjoteConfig.zimfile)


def register_rules():

    ProcessorAssignator.default = config.WikjoteConfig.default_processor

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


def build_pipeline() -> Pipeline:
    logger.info("Building pipeline ...")

    data = osutils.read_json(config.WikjoteConfig.process_input)

    process_pipe = Pipeline(data, config.WikjoteConfig.process_workers_num)

    for handler_conf in config.WikjoteConfig.pipeline:

        handler_info = handler_conf["handler"]
        importer.import_module(handler_info["module_name"], handler_info["is_file"])
        handler = importer.get_class(
            handler_info["module_name"], handler_info["class_name"]
        )
        handler_arguments = handler_conf["arguments"]

        process_pipe.add_handler(handler, handler_arguments)

    return process_pipe


def init_logger():
    logger.setLevel(config.WikjoteConfig.logger_level)

    log_handler = logging.StreamHandler()
    if logger.level == logging.DEBUG:
        formatter = IndentFormatter(
            "[%(levelname)-8s][%(threadName)s]:%(indent)s%(message)s"
        )
    else:
        formatter = logging.Formatter("[%(levelname)-8s][%(threadName)s]: %(message)s")
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)


def print_config():
    config.print_default_config()


def main():
    arguments = parse_args()
    init_config(arguments)
    init_logger()
    init_folders()

    if config.WikjoteConfig.command == "convert":
        register_rules()

        if not arguments.no_download and arguments.zim_path is None:
            download_zim(arguments)

        process_zim()

    if config.WikjoteConfig.command == "process":
        pipeline = build_pipeline()
        pipeline.start()
        # write output
        osutils.write_json(config.WikjoteConfig.process_output, pipeline.get_output())

    logger.info("DONE")


if __name__ == "__main__":
    main()
