import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ProxyWalker.items import ProxyItem


class ProxyroxSpider(CrawlSpider):
    name = 'proxyrox'
    allowed_domains = ['proxyrox.com', 'www.proxyrox.com']
    start_urls = ('https://proxyrox.com/?p=1', )
    rules = (
            Rule(LinkExtractor(restrict_xpaths=('//div[@class="btn-group pager"]/ul/li[last()]/a[@href]')), callback='parse_page',
             follow=True),
    )

    download_delay = 45

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
        trs = response.xpath('//table[@class="table table-striped table-hover"]/tbody/tr')
        if trs:
            for tr in trs:
                item = ProxyItem()
                _ip, _port = tr.xpath('td[1]/a/text()').extract_first().encode().split(':')
                _type = tr.xpath('td[3]/span/text()').extract_first()
                _id = hash(_ip+_port+_type+self.name)
                item['_id'] = _id
                item['source'] = self.name
                item['ip'] = _ip
                item['port'] = _port
                item['p_type'] = _type
                yield item

