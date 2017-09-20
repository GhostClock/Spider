# -*- coding: utf-8 -*-

import re
from datetime import datetime

from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from Spider.items import LagouJobItemLoader, LagouJobItem
from Spider.utils.common import get_md5_Value


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

    # def parse_start_url(self, response):
    #     return []
    #
    # def process_results(self, response, results):
    #     return results

    def parse_job(self, response):
        #   解析拉勾网的职位
        # i = {}
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()

        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)

        item_loader.add_css("title", ".job-name::attr(title)")

        item_loader.add_value("url", response.url)

        item_loader.add_value("url_object_id", get_md5_Value(response.url))

        salary = response.css(".job_request .salary::text").extract()
        salary = re.findall("(\d+)k-(\d+)k", salary[0])
        if salary:
            salary_min = salary[0][0]
            salary_max = salary[0][1]
        else:
            salary_min = 0
            salary_max = 0

        item_loader.add_value("salary_min", salary_min)

        item_loader.add_value("salary_max", salary_max)

        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")

        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")

        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")

        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")

        item_loader.add_css("tags", ".position-label.clearfix li::text")

        item_loader.add_css("pulish_time", ".publish_time::text")

        item_loader.add_css("job_advantage", ".job-advantage p::text")

        item_loader.add_css("job_desc", ".job_bt div")

        item_loader.add_css("job_addr", ".work_addr")

        item_loader.add_css("company_url", "#job_company dt a::attr(href)")

        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")

        item_loader.add_value("crawl_time", datetime.now())

        job_itme = item_loader.load_item()

        return job_itme
