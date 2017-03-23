import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ProxyWalker.items import ProxyItem


class UsProxyspider(CrawlSpider):
    name = 'usproxy'
    allowed_domains = ['us-proxy.org', 'www.us-proxy.org']
    start_urls = ('https://www.us-proxy.org',)

    def make_requests_from_url(self, url):
        return scrapy.http.Request(url,
                                   headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                            'Accept-Encoding': 'gzip, deflate, sdch',
                                            'Connection': 'keep-alive',
                                            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36'
                                            }
                                   )

    def parse_start_url(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        trs = response.xpath('//table[@id="proxylisttable"]/tbody/tr')
        if trs:
            for tr in trs:
                item = ProxyItem()
                _ip = tr.xpath('td[1]/text()').extract_first().encode()
                _port = tr.xpath('td[2]/text()').extract_first().encode()
                _type = tr.xpath('td[5]/text()').extract_first()
                _id = hash(_ip+_port+_type+self.name)
                item['_id'] = _id
                item['source'] = self.name
                item['ip'] = _ip
                item['port'] = _port
                item['p_type'] = _type
                yield item

