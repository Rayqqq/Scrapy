# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class BasicItem(scrapy.Item) :
    source = scrapy.Field()
    _id = scrapy.Field()
    main_record = scrapy.Field()


class ProxyItem(scrapy.Item):
    ip = scrapy.Field()
    port = scrapy.Field()
    source = scrapy.Field()
    _id = scrapy.Field()
    p_type = scrapy.Field()

