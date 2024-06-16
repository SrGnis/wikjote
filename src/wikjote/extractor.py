import logging
import os
import json

from lxml import etree
from lxml.etree import ElementBase
from libzim.reader import Archive

import wikjote.config as config
from wikjote.page import Page
import wikjote.utils.osutils as osutils

logger: logging.Logger = logging.getLogger("wikjote")


def process_zim():
    """Processes ZIM file to extract and convert Wiktionary data.
    
    This function supports both output formats: writing results directly into a JSON array stored in files (nd_output=False) 
    or using a generator yielding one processed entry at a time (nd_output=True).

    Note: The different output methods are a proof of concept, This should be improved.
    """

    logger.info("Starting ZIM processing")

    zim = Archive(config.WikjoteConfig.zimfile)

    if config.WikjoteConfig.lemas is not None:
        lemas = config.WikjoteConfig.lemas
    else:
        # lemas = [entry.title for entry in zim] # not implemented yet see https://github.com/openzim/python-libzim/issues/94
        lemas = [zim._get_entry_by_id(id).title for id in range(zim.all_entry_count)]

    logger.info("%d lemas to process", len(lemas))

    if config.WikjoteConfig.nd_output:

        out_path = os.path.join(config.WikjoteConfig.working_dir, "eswiktionary.ndjson")
        with open(out_path, "w") as output:
            res = yield_loop(lemas, zim)
            for line in res:
                output.write(json.dumps(line, ensure_ascii=False) + "\n")
        logger.info("Processing complete")

    else:
        simple_loop(lemas, zim)


# TODO simplify this


def simple_loop(lemas, zim):
    """
    Processes a list of lemas (lemma titles) and an Archive object `zim` to yield processed page data.
    
    This function iterates through each lemma in the given list, retrieves its corresponding entry from the ZIM archive, 
    processes it into Page objects using the provided `page_process` method and finally writtes the processed data into a JSON file.
    
    Arguments:
    - lemas (list): A list of strings representing lemma titles to process. Spaces in lemma titles are replaced with underscores.
    - zim (Archive): An Archive object from the libzim library, providing access to Wiktionary's ZIM data structure.
    """
    
    res = []
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

            res.append(page.process())

        except Exception as exeption:
            logger.exception('Error processing lema "%s": %s', lema, exeption)

    logger.info("Processing complete")
    logger.info("Writing output into file")
    osutils.write_json(
        os.path.join(config.WikjoteConfig.working_dir, "eswiktionary.json"), res
    )
    logger.info("Writing complete")


def yield_loop(lemas, zim):
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

            res = page.process()

            yield res

        except Exception as exeption:
            logger.exception('Error processing lema "%s": %s', lema, exeption)
