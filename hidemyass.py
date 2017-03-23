# -*- coding:utf-8 -*-
import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ProxyWalker.items import ProxyItem


class HidemyassSpider(CrawlSpider):
    name = 'hidemyass'
    allowed_domains = ['proxylist.hidemyass.com']
    start_urls = ('http://proxylist.hidemyass.com',)
    rules = (
        Rule(LinkExtractor(restrict_xpaths=('/html/body/section/section[4]/section[2]/div/ul/li[last()]/a[@href]')), callback='parse_page', follow=True),
    )

    def parse_start_url(self, response):
        return self.parse(response)

    def parse_page(self, response):
        trs = response.xpath('/html/body/section/section[4]/section/div/table/tbody/tr')
        for tr in trs:
            item = ProxyItem()
            _ip = tr.xpath('td/text()')[1].extract_first().encode()
            _port = tr.xpath('td/text()')[2].extract_first().encode()
            _id = hash(_ip+_port+self.name)
            item['_id'] = _id
            item['source'] = self.name
            item['ip'] = _ip
            item['port'] = _port
            item['p_type'] = _type
            yield item
