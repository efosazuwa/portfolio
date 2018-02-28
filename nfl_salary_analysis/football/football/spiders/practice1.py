import datetime
import socket
import re
import urlparse
import scrapy

from scrapy.loader.processors import MapCompose, Join
#from scrapy.loader import ItemLoader
from scrapy.http.request import Request
#from football.items import FootballItem


class BasicSpider(scrapy.Spider):
    name = "practice1"
    allowed_domains = ("pro-football-reference.com", "www.pro-football-reference.com")


    start_urls = ['http://www.pro-football-reference.com/players']


    def parse(self, response):
        regex = re.compile(r'<!--(.*)-->', re.DOTALL)
        invisible = response.xpath('//comment()').re(regex)
        invisible = ''.join(invisible)
        invisible = scrapy.Selector(text=invisible, type='html')
        invisible = invisible.xpath('//li//@href').extract()
        for url in invisible:
             yield Request(url=urlparse.urljoin(response.url, url))

            #yield Request(url=urlparse.urljoin(response.url, url), callback=self.parse_item)

        item_selector = response.xpath('//div[@id="all_players"]//@href')

        for url in item_selector.extract()[:5]:
            yield Request(url=urlparse.urljoin(response.url, url), callback=self.parse_item1)


            


    def parse_item(self, response):
        num_players = response.xpath('//div/span[@id="players_link"]/@data-label').extract()[0]
        title = response.xpath('//h1/text()').extract()
        yield { 'number': num_players,
                'title': title}

    def parse_item1(self, response):
        name = response.xpath('//h1/text()').extract()
        yield {'name': name}
