import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re

from ProxyWalker.items import ProxyItem


class ProxyListPlusSpider(CrawlSpider):
    name = 'proxylistplus'
    allowed_domains = ['proxylistplus.com', 'list.proxylistplus.com']
    start_urls = ('http://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1',)

    def parse_start_url(self, response):
        return self.parse_page(response)

    def parse_page(self, response):
        trs = response.xpath('/html/body/div[1]/table[2]/tr')
        trs = trs[2:]
        if trs:
            for tr in trs:
                item = ProxyItem()
                try:
                    _ip = tr.xpath('td[2]/text()').extract_first().encode()
                    _ip = re.search('(\d+\.\d+\.\d+\.\d+)', _ip).group(1)
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
        pages = response.xpath('/html/body/div[1]/table[3]/tr/td/a/@href').extract()
        if pages:
            this_page = response.url.split('//')[-1].split('/')[-1]
            if not this_page or this_page == 'list.proxylistplus.com' or this_page == u'' or this_page == '':
                this_page = 'Fresh-HTTP-Proxy-List-1'
            next_page = 'Fresh-HTTP-Proxy-List-%d' % (int(this_page[-1])+1)
            next_page = next_page.decode()
            if next_page in pages:
                next_page.encode()
                yield scrapy.http.Request('http://list.proxylistplus.com/'+next_page, callback=self.parse_page)


