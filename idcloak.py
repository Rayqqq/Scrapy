import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ProxyWalker.items import ProxyItem


class Ip004Spider(CrawlSpider):
    name = 'idcloak'
    allowed_domains = ['idcloak.com', 'www.idcloak.com']
    start_urls = ('http://www.idcloak.com/proxylist/free-proxy-ip-list.html',)

    def parse_start_url(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        trs = response.xpath('//table[@id="sort"]/tr')
        trs = trs[1:]
        if trs:
            for tr in trs:
                item = ProxyItem()
                try:
                    _ip = tr.xpath('td[last()]/text()').extract_first().encode()
                    _port = tr.xpath('td[last()-1]/text()').extract_first().encode()
                    _type = tr.xpath('td[last()-3]/text()').extract_first()
                    _id = hash(_ip+_port+_type+self.name)
                    item['_id'] = _id
                    item['source'] = self.name
                    item['ip'] = _ip
                    item['port'] = _port
                    item['p_type'] = _type
                    yield item
                except:
                    pass
        try:
            next_page = response.xpath('//input[@type="submit"][@name="page"][@class="this_page"]/following::input[@name="page"][@value][1]/@value').extract_first().encode()
            if next_page:
                yield scrapy.http.FormRequest('http://www.idcloak.com/proxylist/free-proxy-ip-list.html#sort',
                        formdata={'port[]':'all', 'protocol-http':'true', 'protocol-https': 'true',
                                  'protocol-sock4': 'true', 'protocol-sock5': 'true', 'anonymity-low': 'true', 
                                  'anonymity-medium': 'true', 'anonymity-high': 'true', 'connection-low': 'true',
                                  'connection-medium': 'true', 'connection-high': 'true', 'speed-low': 'true',
                                  'speed-medium': 'true', 'speed-high': 'true', 'order': 'desc', 'by': 'updated',
                                  'page': next_page}, callback=self.parse_page)
        except:
            pass

