import datetime
import socket
import re
import urlparse
import scrapy
import utils

from scrapy.loader.processors import MapCompose, Join
#from scrapy.loader import ItemLoader
from scrapy.http.request import Request
#from football.items import FootballItem


class BasicSpider(scrapy.Spider):
    name = "stat_collector"
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

        item_selector = response.xpath('//div[@id="all_players"]//@href')

        for url in item_selector.extract():
            yield Request(url=urlparse.urljoin(response.url, url), callback=self.parse_item)





    def parse_item(self, response):
        visible_tables = response.xpath('//div//table//@id').extract()
        endlist=[]
        dic = {}
        dic['name'] = response.xpath('//h1[@itemprop="name"]/text()').extract()
        dic['height'] = response.xpath('//*[@itemprop="height"]/text()').extract()
        dic['weight'] = response.xpath('//*[@itemprop="weight"]/text()').extract()
        dic['birthday'] = response.xpath('//span[@id="necro-birth"]/@data-birth').extract()
        dic['draft'] = response.xpath('//*[contains(strong, "Draft")]//parent::p/text()').extract()
        #response.xpath('//*[@id="{}"]/ancestor::table/@id'.format(visible_tables[0]).extract()
        key = visible_tables[0]
        dic[key] = {}

        for x in visible_tables[1:]:
            key = response.xpath('//*[@id="{}"]/ancestor::table/@id'.format(x)).extract()[0]
            dic[key][x]=[]
            for y in utils.html_tags['{}'.format(visible_tables[0])]:
                dic[key][x].append({y: response.xpath('//*[@id="{}"]//*[@data-stat="{}"]//text()'.format(x, y)).extract()})

        regex = re.compile(r'<!--(.*)-->', re.DOTALL)
        invisible_tables = response.xpath('//comment()').re(regex)
        invisible_tables = ''.join(invisible_tables)
        invisible_tables = scrapy.Selector(text=invisible_tables, type='html')
        keys = invisible_tables.xpath('//div//table/@id').extract()
        correct_keys = [x for x in keys if x in utils.html_tags]
        special = ['fantasy', 'all_pro']
        correct_keys = [x for x in correct_keys if x not in special]
        for key in correct_keys:
            dic[key] = {}

        for key in correct_keys:
            rows = invisible_tables.xpath('//*[@id="{}"]//tbody//@id'.format(key)).extract()
            for x in rows:
                k = invisible_tables.xpath('//*[@id="{}"]//*[@id="{}"]/ancestor::table/@id'.format(key, x)).extract()[0]
                dic[k][x] = []
                for y in utils.html_tags['{}'.format(k)]:
                    dic[k][x].append({y: invisible_tables.xpath('//*[@id="{}"]//*[@id="{}"]//*[@data-stat="{}"]//text()'.format(key, x, y)).extract()})

        pic={}
        for k in special:
            pic[k] = {}
            for x in invisible_tables.xpath('//*[@id="{}"]//tbody//tr'.format(k)):
                if k=='fantasy':
                    key = x.xpath('*[@data-stat="year_id"]//text()').extract()[0]
                else:
                    key = x.xpath('*[@data-stat="year"]//text()').extract()[0] + ' ' + x.xpath('*[@data-stat="voters"]//text()').extract()[0]
                pic[k][key] = pic.get((k,key), [])
                for y in utils.html_tags['{}'.format(k)]:
                    pic[k][key].append({y: x.xpath('*[@data-stat="{}"]//text()'.format(y)).extract()})

        def merge_dicts(x, y):
            z = x.copy()
            z.update(y)
            return z
        return merge_dicts(dic, pic)
