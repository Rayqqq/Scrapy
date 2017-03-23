import json
import scrapy
import PyV8
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ProxyWalker.items import ProxyItem


class NNTimeSpider(CrawlSpider):
    name = 'nntime'
    allowed_domains = ['nntime.com', 'www.nntime.com']
    start_urls = ('http://nntime.com/proxy-ip-01.htm',)
    rules = (
        Rule(LinkExtractor(restrict_xpaths=('//div[@id="navigation"]/a[last()][@href]')), callback='parse_page',
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
        _port_expr_values = response.xpath('//script[2]/text()').extract_first().encode()[1:]
        trs = response.xpath('//table[@id="proxylist"]/tr')
        if response.url == 'http://nntime.com/proxy-ip-01.htm':
            trs = trs[1:]
        if trs:
            for tr in trs:
                item = ProxyItem()
                _ip = tr.xpath('td[2]/text()').extract_first().encode()
                _port_expr = tr.xpath('td[2]//script/text()').extract_first().encode().split('":"')[1][1:-1].split('+')
                with PyV8.JSContext() as env:
                    env.eval(_port_expr_values)
                    _port = ''
                    for expr in _port_expr:
                        _port += str(env.eval(expr))
                _type = tr.xpath('td[3]/text()').extract_first()
                _id = hash(_ip+_port+_type+self.name)
                item['_id'] = _id
                item['source'] = self.name
                item['ip'] = _ip
                item['port'] = _port
                item['p_type'] = _type
                yield item

