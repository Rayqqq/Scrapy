import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ProxyWalker.items import ProxyItem


class Ip004Spider(CrawlSpider):
    name = 'ip004'
    allowed_domains = ['ip004.com', 'www.ip004.com']
    start_urls = ('http://ip004.com',)
    rules = (
        Rule(LinkExtractor(restrict_xpaths=('//div[@class="pagination"]/div/a[last()][@href]')), callback='parse_page',
             follow=True),
    )

    def parse_start_url(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        tables = response.xpath('//table[@id="proxytable"]')
        trs = tables[1].xpath('tr')
        trs = trs[1:]
        if trs:
            for tr in trs:
                item = ProxyItem()
                try:
                    _ip = tr.xpath('td[1]/a/text()').extract_first().encode()
                    _port = tr.xpath('td[2]/text()').extract_first().encode()
                    _type = tr.xpath('td[3]/text()').extract_first()
                    _id = hash(_ip+_port+_type+self.name)
                    item['_id'] = _id
                    item['source'] = self.name
                    item['ip'] = _ip
                    item['port'] = _port
                    item['p_type'] = _type
                    yield item
                except:
                    pass
