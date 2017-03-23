import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ProxyWalker.items import ProxyItem


class ProxyDbSpider(CrawlSpider):
    name = 'proxydb'
    allowed_domains = ['proxydb.net', ]
    start_urls = ('http://proxydb.net/list', )
    rules = (
            Rule(LinkExtractor(restrict_xpaths=('//nav[@class="mb"]/ul/li[@class="active"]/following::li[1]/a[@href]')), callback='parse_page',
             follow=True),
    )

    #download_delay = 45

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
        trs = response.xpath('//table[@class="table table-hover table-condensed"]/tbody/tr')
        if trs:
            for tr in trs:
                item = ProxyItem()
                _ip = tr.xpath('td[1]/a/text()').extract_first().encode()
                _port = tr.xpath('td[2]/text()').extract_first().encode()
                _type = tr.xpath('td[8]/abbr/text()').extract_first().encode()
                _id = hash(_ip+_port+_type+self.name)
                item['_id'] = _id
                item['source'] = self.name
                item['ip'] = _ip
                item['port'] = _port.strip()
                item['p_type'] = _type
                yield item

