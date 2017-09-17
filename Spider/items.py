# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join


class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #   拉勾网职位信息
    title = scrapy.Field()

    url = scrapy.Field()

    uil_object_id = scrapy.Field()

    salary_min = scrapy.Field()

    salary_max = scrapy.Field()

    job_city = scrapy.Field()

    work_years = scrapy.Field()

    degree_need = scrapy.Field()

    job_type = scrapy.Field()

    pulish_time = scrapy.Field()

    tags = scrapy.Field()

    job_advantage = scrapy.Field()

    job_desc = scrapy.Field()

    job_addr = scrapy.Field()

    company_url = scrapy.Field()

    company_name = scrapy.Field()

    crawl_time = scrapy.Field()

    # crawl_update_time = scrapy.Field()