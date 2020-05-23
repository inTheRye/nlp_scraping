# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NlpScrapingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    published_date = scrapy.Field()
    title = scrapy.Field()
    text = scrapy.Field()
    url = scrapy.Field()
    tags = scrapy.Field()
    keywords = scrapy.Field()