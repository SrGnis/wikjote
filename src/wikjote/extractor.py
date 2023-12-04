import json
import logging
import os
import traceback

import config
from page import Page

from lxml import etree
from lxml.etree import ElementBase
from libzim.reader import Archive

logger: logging.Logger = logging.getLogger("wikjote")


def process_zim():
    logger.info("Starting ZIM processing")

    zim = Archive(config.zimfile)

    # titles = [entry.title for entry in zim] not implemented yet
    # titles = [zim._get_entry_by_id(id).title for id in range(zim.all_entry_count)] TODO: allow using this

    with open(
        os.path.join(config.downloads_dir, "eswiktionary-titles"), encoding="utf8"
    ) as lemas_file:
        lemas = lemas_file.readlines()
        # lemas = ["Tea"]

        logger.info("%d lemas to process", len(lemas))
        for lema in lemas:
            lema = lema.strip()
            logger.debug('Processing: "%s"', lema)
            try:
                lema = lema.strip()
                entry = zim.get_entry_by_path(lema)
                entry_content = bytes(entry.get_item().content).decode("UTF-8")
                entry_html: ElementBase = etree.HTML(entry_content)  # type: ignore

                page = Page(entry_html, lema)

                page.process()

            except Exception:
                logger.exception('Error processing lema "%s"', lema)


def save_page(page_html: str, lema: str):
    with open(
        os.path.join(config.working_dir, lema + ".html"), "w", encoding="UTF-8"
    ) as file:
        file.write(page_html)
