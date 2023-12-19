import logging
import os

from lxml import etree
from lxml.etree import ElementBase
from libzim.reader import Archive

import wikjote.config as config
from wikjote.page import Page
import wikjote.utils.osutils as osutils

logger: logging.Logger = logging.getLogger("wikjote")


def process_zim():
    logger.info("Starting ZIM processing")

    zim = Archive(config.WikjoteConfig.zimfile)

    res = {}

    if config.WikjoteConfig.lemas is not None:
        lemas = config.WikjoteConfig.lemas
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
            logger.exception('Error processing lema "%s": %s', lema, exeption)

    logger.info("Processing complete")
    logger.info("Writing output into file")
    osutils.write_json(
        os.path.join(config.WikjoteConfig.working_dir, "eswiktionary.json"), res
    )
    logger.info("Writing complete")
