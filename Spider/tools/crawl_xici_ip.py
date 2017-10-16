# -*- coding=utf-8 -*-
__author__ = 'ghostclock'
import requests
from scrapy.selector import Selector
import pymysql

conn = pymysql.connect(host='192.168.0.100', user='root', password='admin123', db = 'article_spider', charset='utf8')
cursor = conn.cursor()

def crawl_ips():
    #   爬取西刺的免费ip
    header = {
        "User-Agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    }
    for i in range(2447):
        url = "http://www.xicidaili.com/nn/{0}".format(i + 1)
        re = requests.get(url, headers=header)
        selector = Selector(text=re.text)
        all_trs = selector.xpath('//table[@id="ip_list"]/tr')
        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.xpath('td[@class="country"]/div/@title').extract()[0]
            if speed_str:
                speed = float(speed_str.split("秒")[0])

            all_texts = tr.xpath('td/text()').extract()
            if all_texts:
                ip = all_texts[0]
                port = all_texts[1]
                proxy_type = all_texts[5]

            ip_list.append((ip, port, proxy_type, speed))
        print(url, '\n ', ip_list)
        for ip_info in ip_list:
            insert_sql = "insert proxy_ip(ip, port, speed, proxy_type) VALUES ('{0}', '{1}', {2}, '{3}')".format(
                ip_info[0], ip_info[1], ip_info[3], ip_info[2])
            try:
                cursor.execute(insert_sql)
                conn.commit()
            except IOError as error:
                print(error)


if __name__ == '__main__':
    crawl_ips()
