# TODO: senses could be all in a single dl tag
xpathqueries = {
    'wiktionary_es_download_links': './/a[contains(text(),"wiktionary_es_all_nopic") ]',
    'es_section': '//h2[@id="Español"]/parent::summary/parent::details',
    'categories': './/details/dl/parent::details',
    'category': './/summary/*[self::h1 | self::h2 | self::h3 | self::h4 | self::h5]',
    'flection': './/table[@class="inflection-table"]',
    'senses': './/dl',
    'sense_head': './/dt',
    'sense_content': './/dd',
    'locutions': './/h3[@id="Locuciones"]/parent::summary/parent::details',
    'additional_info': './/h3[@id="Información_adicional"]/parent::summary/parent::details',
    'tranlations': './/h3[@id="Traducciones"]/parent::summary/parent::details',
}