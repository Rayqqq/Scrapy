import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
import PyV8
from scrapy.linkextractors import LinkExtractor

from ProxyWalker.items import ProxyItem


class ChnlankerSpider(CrawlSpider):
    name = 'spys'
    allowed_domains = ['spsys.ru']

    def start_requests(self):
        return [ scrapy.http.FormRequest('http://spys.ru/en/free-proxy-list/', formdata={'xpp':'3','xf1':'0','xf2':'0','xf4':'0'}, callback=self.parse_page)]

    def parse_page(self, response):
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        trs = response.xpath('//table[2]/tr[4]/td[1]/table/tr')
        _port_expr_values = response.xpath('/html/body/script[1]/text()').extract_first()
        trs = trs[3:]
        if trs:
            for tr in trs:
                item = ProxyItem()
                try:
                    _ip = tr.xpath('td[1]/font[2]/text()').extract_first().encode()
                    _port_expr = trs[3].xpath('td[1]/font/script/text()').extract_first().encode().split('"+')[1][:-1]
                    _port_expr = _port_expr.split('+')
                    with PyV8.JSContext() as env:
                        env.eval(_port_expr_values)
                        _port = ''
                        for expr in _port_expr:
                            _port += str(env.eval(expr))

                    _type = tr.xpath('td[3]/a/font/text()').extract_first()
                    _id = hash(_ip+_port+_type+self.name)
                    item['_id'] = _id
                    item['source'] = self.name
                    item['ip'] = _ip
                    item['port'] = _port
                    item['p_type'] = _type
                    yield item
                except:
                    pass
