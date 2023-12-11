import json
import logging
import os

import config
from page import Page
import utils.osutils as osutils

from lxml import etree
from lxml.etree import ElementBase
from libzim.reader import Archive

logger: logging.Logger = logging.getLogger("wikjote")


def process_zim():
    logger.info("Starting ZIM processing")

    zim = Archive(config.zimfile)

    res = {}

    if config.lemas is not None:
        lemas = config.lemas
    else:
        # lemas = [entry.title for entry in zim] not implemented yet
        lemas = [zim._get_entry_by_id(id).title for id in range(zim.all_entry_count)]

    logger.info("%d lemas to process", len(lemas))
    for lema in lemas:
        lema: str = lema.strip()
        lema = lema.replace(" ", "_")  # spaces in lema titles are replaced by '_'
        logger.debug('Processing: "%s"', lema)
        try:
            lema = lema.strip()
            entry = zim.get_entry_by_path(lema)
            entry_content = bytes(entry.get_item().content).decode("UTF-8")
            entry_html: ElementBase = etree.HTML(entry_content)  # type: ignore

            page = Page(entry_html, lema)

            res[lema] = page.process()

        except Exception as exeption:
            logger.error('Error processing lema "%s": %s', lema, exeption)

    logger.info("Processing complete")
    logger.info("Writing output into file")
    osutils.write_json(os.path.join(config.working_dir, "eswiktionary.json"), res)
    logger.info("Writing complete")


def save_page(page_html: str, lema: str):
    osutils.write_file(os.path.join(config.working_dir, lema + ".html"), page_html)
