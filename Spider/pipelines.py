# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import pymysql.cursors
from twisted.enterprise import adbapi


class SpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlTwistedPiplines(object):
    """
    用Twisted框架来异步插入数据
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, setting):
        dbparms = dict(
            host=setting['MYSQL_HOST'],
            db=setting['MYSQL_DB_NAME'],
            user=setting['MYSQL_USER'],
            passwd=setting['MYSQL_PASSWORD'],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failuer, item, spider):
        # 异常处理
        print(failuer.value)

    def do_insert(self, cursor, item):
        # 插入到数据库
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)