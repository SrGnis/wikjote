"""
A dict of XPath queries for easy usage.

Note: In the future this should be replaced by a dedicated Repository class or something like that.
"""
xpathqueries = {
    "wiktionary_es_download_links": './/a[contains(text(),"wiktionary_es_all_nopic") ]',
    "language_section_chosed": '//h2[@id="{}"]/parent::summary/parent::details',
    "language_sections": '//h2/parent::summary/parent::details',
    "first_sections": '//h2/parent::summary/parent::details',
    "sense_sections": "//details[child::dl]",
    "inner_sections": "./details",
    "categories": "./details/dl/parent::details",
    "section_name": "./summary/*[self::h1 | self::h2 | self::h3 | self::h4 | self::h5]",
    "flection": './/table[contains(@class,"inflection-table")]',
    "sense_v2": "./dl/*[self::dt | self:: dd]",
    "senses": "./dl",
    "senses_elements": "./dl/*[self::dt | self::dd]",
    "sense_title": "./dt",
    "sense_content": "./dd",
    "sense_attributes": ".//dd/ul",
    "sense_attributes_wrong": "./following-sibling::ul[count(preceding-sibling::dl)={}]",
    "locutions": './/h3[@id="Locuciones"]/parent::summary/parent::details',
    "additional_info": './/h3[@id="Información_adicional"]/parent::summary/parent::details',
    "tranlations": './/h3[@id="Traducciones"]/parent::summary/parent::details',
    "conjugation": '//h3[@id="Conjugación"]/parent::summary/parent::details',
    "language_section_rule": './descendant::*[@class="headline-lang"]',
    "sense_section_rule": "./child::dl",
}
