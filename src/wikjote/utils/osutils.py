import json
import os
import logging

logger: logging.Logger = logging.getLogger("wikjote")


def mkdir_if_not_exists(path: str):
    if not os.path.exists(path):
        logger.info("Creating folder %s", path)
        os.mkdir(path)


def write_file(path, contents):
    out_file = open(path, encoding="utf8", mode="w")
    out_file.write(contents)
    out_file.close()


def write_json(path, obj: object):
    contents = json.dumps(obj, ensure_ascii=False, indent=2)
    write_file(path, contents)


def read_list(path):
    file = open(path)
    data = file.read().splitlines()
    file.close()

    return data


def read_json(path):
    file = open(path)
    data = json.load(file)
    file.close()

    return data
