# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags
from Spider.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

class SpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def remove_splash(value):
    # 去掉城市的斜杠
    return value.replace("/", "")


def get_pulish_time(value):
    # 获取发布时间
    return value.split(" ")[0]


def handle_jobaddr(value):
    # 处理多余的空格和\n 并且用 - 格式化
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    address = re.compile(" -|- ").sub("-", "".join(addr_list))
    return address


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    #   拉勾网职位信息
    title = scrapy.Field()

    url = scrapy.Field()

    uil_object_id = scrapy.Field()

    salary_min = scrapy.Field()

    salary_max = scrapy.Field()

    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )

    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )

    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )

    job_type = scrapy.Field()

    pulish_time = scrapy.Field(
        input_processor=MapCompose(get_pulish_time)
    )

    tags = scrapy.Field(
        input_processor=Join(",")
    )

    job_advantage = scrapy.Field()

    job_desc = scrapy.Field()

    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr)
    )

    company_url = scrapy.Field()

    company_name = scrapy.Field()

    crawl_time = scrapy.Field()

    # crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            INSERT INTO lagou_job(
                title, url, uil_object_id, salary_min, 
                salary_max, job_city, work_years, 
                degree_need, job_type, pulish_time, 
                tags, job_advantage, job_desc, 
                job_addr, company_url, company_name, 
                crawl_time) 
            VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON DUPLICATE KEY UPDATE 
            salary_min=VALUES(salary_min), salary_max=VALUES(salary_max),
            work_years=VALUES(work_years), degree_need=VALUES(degree_need),
            job_type=VALUES(job_type), pulish_time=VALUES(pulish_time),
            tags=VALUES(tags), job_advantage=VALUES(job_advantage),
            job_desc=VALUES(job_desc)
        """

        params = (
            self['title'], self['url'], self['uil_object_id'],
            self['salary_min'], self['salary_max'], self['job_city'],
            self['work_years'], self['degree_need'], self['job_type'],
            self['pulish_time'], self['tags'], self['job_advantage'],
            self['job_desc'], self['job_addr'], self['company_url'],
            self['company_name'], self['crawl_time'].strftime(SQL_DATETIME_FORMAT))

        return insert_sql, params