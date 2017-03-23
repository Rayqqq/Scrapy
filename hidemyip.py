import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ProxyWalker.items import ProxyItem


class HideMyIpSpider(CrawlSpider):
    name = 'hidemyip'
    allowed_domains = ['hide-my-ip.com', 'www.hide-my-ip.com']
    start_urls = ('https://www.hide-my-ip.com/proxylist.shtml',)

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
        ips = json.loads(response.xpath('//script[@type="text/javascript"][3]/text()').extract_first().encode().split(';')[0][13:])
        if ips:
            for ip in ips:
                item = ProxyItem()
                _ip = ip[u'i'].encode()
                _port = ip[u'p'].encode()
                _type = ip[u'a'].encode()
                _id = hash(_ip+_port+_type+self.name)
                item['_id'] = _id
                item['source'] = self.name
                item['ip'] = _ip
                item['port'] = _port
                item['p_type'] = _type
                yield item

