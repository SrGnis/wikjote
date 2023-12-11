import requests
import logging
import time

from lxml import etree
from lxml.etree import ElementBase
from exceptions import WrongHTTPResponseCode, XMLNotFound
from queries import xpathqueries

logger: logging.Logger = logging.getLogger("wikjote")


def download_last_zim(destination: str):
    logger.info("Getting last zim url")
    # TODO: add mirrors
    url = "https://download.kiwix.org/zim/wiktionary/"
    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        logger.error("ZIM download page not found")
        raise WrongHTTPResponseCode(response.status_code, 200, url)
    page = response.text

    # find the download links and select get the latest one
    html: ElementBase = etree.HTML(page)  # type: ignore
    links: list[ElementBase] = html.xpath(
        xpathqueries.get("wiktionary_es_download_links")
    )
    if len(links) == 0:
        logger.error("No zim download link found")
        raise XMLNotFound(ElementBase.__module__ + "." + ElementBase.__name__)
    links.sort(key=lambda link: link.text)
    zim_url = url + links.pop().text

    download_file(zim_url, destination)


def download_file(url: str, destination: str):
    logger.info("Downloading file: %s, to %s", url, destination)
    r = requests.get(url, stream=True, timeout=10)
    response_lenght = int(r.headers["Content-length"])
    downloaded = 0
    logger.info(
        "Downloading: %s / %s",
        format_bytes(downloaded),
        format_bytes(response_lenght),
    )
    moment = time.time()
    with open(destination, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            fd.write(chunk)
            downloaded += len(chunk)
            now = time.time()
            if now - moment > 2 or downloaded == response_lenght:
                logger.info(
                    "Downloading: %s / %s",
                    format_bytes(downloaded),
                    format_bytes(response_lenght),
                )
                moment = now


def format_bytes(size):
    power = 2**10
    n = 0
    power_labels = {0: "", 1: "K", 2: "M", 3: "G", 4: "T"}
    while size > power:
        size /= power
        n += 1
    return f"{size:.1f}" + power_labels[n] + "B"
