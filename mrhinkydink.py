import json
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from ProxyWalker.items import ProxyItem


class MrhinkydinkSpider(CrawlSpider):
    name = 'mrhinkydink'
    allowed_domains = ['mrhinkydink.com', 'www.mrhinkydink.com']
    start_urls = ('http://www.mrhinkydink.com/proxies.htm',)

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
        trs = response.xpath('//table')[4].xpath('tr')
        trs = trs[3:-4]
        if trs:
            for tr in trs:
                item = ProxyItem()
                _ip = tr.xpath('td[1]/text()').extract_first().encode()
                _port = tr.xpath('td[2]/text()').extract_first().encode()
                _type = tr.xpath('td[3]/text()').extract_first()
                _id = hash(_ip+_port+_type+self.name)
                item['_id'] = _id
                item['source'] = self.name
                item['ip'] = _ip
                item['port'] = _port
                item['p_type'] = _type
                yield item
        urls = response.xpath('//table')[4].xpath('tr[last()]/td/a[@href]/@href').extract()
        this_page = response.url
        if this_page == 'http://www.mrhinkydink.com/proxies.htm':
            this_page = 'http://www.mrhinkydink.com/proxies1.htm'
        this_page = this_page[-5]
        next_page = int(this_page) + 1
        next_page = u'proxies%d.htm' % next_page
        yield scrapy.http.Request('http://www.mrhinkydink.com/'+next_page.encode(), callback=self.parse_page)
