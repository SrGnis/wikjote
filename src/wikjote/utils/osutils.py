import os
import logging

logger: logging.Logger = logging.getLogger("wikjote")


def mkdir_if_not_exists(path: str):
    if not os.path.exists(path):
        logger.info("Creating folder %s", path)
        os.mkdir(path)
