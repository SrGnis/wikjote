xpathqueries = {
    "wiktionary_es_download_links": './/a[contains(text(),"wiktionary_es_all_nopic") ]',
    "language_section_chosed": '//h2[@id="{}"]/parent::section',  # deprecated
    "language_sections": '//section[descendant::*[@class="headline-lang"]]',
    "first_sections": '//section[descendant::*[@class="headline-lang"]]',
    # "first_sections": '//h2[@id="Español"]/parent::section',
    "sense_sections": "//section[child::dl]",
    "inner_sections": "./section",
    "categories": "./section/dl/parent::section",  # not used
    "section_name": "./*[self::h1 | self::h2 | self::h3 | self::h4 | self::h5]",
    "flection": './/table[contains(@class,"inflection-table")]',
    "senses": "./dl",
    "sense_title": "./dt",
    "sense_content": "./dd",
    "sense_attributes": ".//dd/ul",
    "sense_attributes_wrong": "./following-sibling::ul[count(preceding-sibling::dl)={}]",
    "locutions": './/h3[@id="Locuciones"]/parent::section',
    "additional_info": './/h3[@id="Información_adicional"]/parent::section',
    "tranlations": './/h3[@id="Traducciones"]/parent::section',
    "conjugation": '//h3[@id="Conjugación"]/parent::section',
    "language_section_rule": './descendant::*[@class="headline-lang"]',
    "sense_section_rule": "./child::dl",
}
