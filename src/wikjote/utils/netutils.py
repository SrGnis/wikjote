import requests
from lxml import etree
from lxml.etree import _Element
from exceptions import WrongHTTPResponseCode, XMLNotFound
from queries import xpathqueries

def download_last_zim(destination: str):
    # TODO: add mirrors
    url = 'https://download.kiwix.org/zim/wiktionary/'
    response = requests.get(url)
    if(response.status_code != 200):
        raise WrongHTTPResponseCode(response.status_code, 200, url)
    page = response.text
    
    # find the download links and select get the latest one
    html: _Element = etree.HTML(page) # type: ignore 
    links: list[_Element] = html.xpath(xpathqueries.get('wiktionary_es_download_links'))
    if(len(links) == 0):
        raise XMLNotFound(_Element.__module__ + '.' + _Element.__name__)
    links.sort(key=lambda link: link.text)
    zim_url = url + links.pop().text
       
    download_file(zim_url, destination)

def download_file(url: str, destination: str):
    r = requests.get(url, stream=True)
    with open(destination, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    