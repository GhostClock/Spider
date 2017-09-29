# -*- coding: utf-8 -*-
import scrapy
import re
import time
import json

from scrapy.http import FormRequest, Request
from Spider.utils.zheye import zheye

try:
    import urlparse as parse
except:
    from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    user_agent_FireFox = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    headers = {
        "Host": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": user_agent_FireFox
    }

    # 1.
    def start_requests(self):
        """
        第一次请求,获取xsrf
        """
        return [FormRequest(url="https://www.zhihu.com/#signin",
                            headers=self.headers, callback=self.get_xsrf)]

    # 2.
    def get_xsrf(self, response):
        """
        解析xsrf，请求中文验证码
        """
        match_obj = re.match(b'.*name="_xsrf" value="(.*?)"',
                           response.body, re.DOTALL)
        xsrf = ""
        if match_obj:
            xsrf = match_obj.group(1)

        time_date = str(int(time.time() * 1000))
        captcha_url = "https://www.zhihu.com/captcha.gif?r={}&type=login&lang=cn".format(time_date)
        return Request(url=captcha_url, headers=self.headers,
                       meta={"xsrf": xsrf}, callback=self.login_cn)

    # 3.
    def login_cn(self, response):
        """
        开始登录
        """
        post_url = "https://www.zhihu.com/login/email"
        post_data = {
            "_xsrf": response.meta["xsrf"],
            "email": "",
            "password": "",
            "captcha": self.get_captcha(response),
            "captcha_type": "cn"
        }
        return [FormRequest(url=post_url,
                            formdata=post_data,
                            headers=self.headers,
                            callback=self.check_login)]

    # 4.
    def get_captcha(self, response):
        """
        获取验证码，并进行格式化
        """
        with open("captcha.gif", "wb") as f:
            f.write(response.body)
            f.close()
        z = zheye()
        positions = z.Recognize("captcha.gif")  # 返回的tuple的第二个值是x坐标，第一个值是y坐标，笛卡尔坐标系 [(y, x), (y, x)
        print(positions)

        poss = []
        if len(positions) == 2:
            if positions[0][1] > positions[1][1]:
                poss.append([positions[1][1] / 2, positions[1][0] / 2])
                poss.append([positions[0][1] / 2, positions[0][0] / 2])
            else:
                poss.append([positions[0][1] / 2, positions[0][0] / 2])
                poss.append([positions[1][1] / 2, positions[1][0] / 2])
        else:
            poss.append([positions[0][1], positions[0][0]])
        print("处理后的坐标 ", poss)

        captcha_str = '{"img_size": [200, 44], "input_points": %s}' % poss
        print("captcha_str ", captcha_str)
        return captcha_str

    # 5.
    def check_login(self, response):
        """
        检查登录状态
        """
        text_json = json.loads(response.text)
        print(text_json['msg'])

        if "msg" in text_json and "登录成功" == text_json["msg"]:
            for url in self.start_urls:
                # 6.
                yield Request(url, dont_filter=True, headers=self.headers) # 这里没写回调函数，会默认回到parse函数

    def parse(self, response):
        """
        深度优先 - 提取出html页面中所有url 并跟踪这些URL并进一步爬取
        如果提取的URL中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]

        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)

        # 获得过滤后的url
        for url in all_urls:
            print(url)



