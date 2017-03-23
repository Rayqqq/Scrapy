# 定义一个爬虫
#XPath is a language for selecting nodes in XML documents, which can also be used with HTML.
#CSS is a language for applying styles to HTML documents. It defines selectors to associate those styles with specific HTML elements
import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from ProxyWalker.items import ProxyItem


class ChnlankerSpider(CrawlSpider):
    name = 'chnlanker'   # 爬虫的名字
    allowed_domains = ['proxy.chnlanker.com',]
    start_urls = ('http://proxy.chnlanker.com/?t=anonymous', 'http://proxy.chnlanker.com/?t=hightanonymous',
                  'http://proxy.chnlanker.com/?t=transparent')  // define-request-link最开始爬取的地址

    def parse_start_url(self, response):    #这个方法负责解析返回的数据、匹配抓取的数据(解析为 item )并跟踪更多的 URL
        return self.parse(response)

    def parse(self, response):                #scrapy selector
        trs = response.xpath('//table/tr')
        trs = trs[1:]
        if trs:
            for tr in trs:
                item = ProxyItem()
                try:
                    _ip = tr.xpath('td[2]/text()').extract_first().encode()
                    _port = tr.xpath('td[3]/text()').extract_first().encode()
                    _type = tr.xpath('td[4]/text()').extract_first()
                    _id = hash(_ip+_port+_type+self.name)
                    item['_id'] = _id
                    item['source'] = self.name
                    item['ip'] = _ip
                    item['port'] = _port
                    item['p_type'] = _type
                    yield item
                except:
                    pass
