#-*- coding:utf8 -*-

import time
import hashlib  #md5编码
from scrapy import signals
from ProxyWalker.signals import item_exists

class Signals(object) :
    def __init__(self, crawler):
        self.crawler = crawler
        self.max_count = crawler.settings.getint('CLOSESPIDER_AFTER_COUNT_ITEMS_DROPPED')
        self.counter = 0

        crawler.signals.connect(self.item_exists, signal=item_exists)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def item_exists(self, item, spider):
        print '[*] main record of log id:%s exists' % item['_id']
        self.counter += 1
        if self.counter >= self.max_count:
            #等待30s,等待未完成的任务
            self.crawler.engine.close_spider(spider, '[!] Got %d items dropped, fetch stop.' % self.max_count)

