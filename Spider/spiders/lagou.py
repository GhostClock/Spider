# -*- coding: utf-8 -*-

import os
import json
import re
import requests
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request, FormRequest
from time import time
from PIL import Image
from hashlib import md5
from Spider.settings import DEFAULT_REQUEST_HEADERS
try:
    import cookielib
except:
    import http.cookiejar as cookielib

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com']
    start_urls = ['https://www.lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=('zhaopin/.*', )), follow=True),
        Rule(LinkExtractor(allow=('gongsi/j\d+.html', )), follow=True),
        # 如果连接满足下面这种形式，就会调到callback里面的方法去支持 allow里面传递的是正则表达式
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    def parse_start_url(self, response):
        return []

    def process_results(self, response, results):
        return results

    def parse_job(self, response):
        #   解析拉勾网的职位
        i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
