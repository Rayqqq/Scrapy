import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ProxyWalker.items import ProxyItem


class FreeproxylistSpider(CrawlSpider):
    name = 'freeproxylist'
    allowed_domains = ['free-proxy-list.net']
    start_urls = ('http://free-proxy-list.net',)

    def parse_start_url(self, response):
        return self.parse(response)

    def parse(self, response):
        trs = response.xpath('//table/tbody/tr')
        if trs:
            for tr in trs:
                item = ProxyItem()
                try:
                    _ip = tr.xpath('td[1]/text()').extract_first().encode()
                    _port = tr.xpath('td[2]/text()').extract_first().encode()
                    _type = tr.xpath('td[5]/text()').extract_first().encode()
                    _id = hash(_ip+_port+_type+self.name)
                    item['_id'] = _id
                    item['source'] = self.name
                    item['ip'] = _ip
                    item['port'] = _port
                    item['p_type'] = _type
                    yield item
                except:
                    pass
