# -*- coding: utf-8 -*-
import scrapy
import re
import time
import json
import datetime, random
from scrapy.http import FormRequest, Request
from Spider.utils.zheye import zheye
from scrapy.loader import ItemLoader
from Spider.items import ZhihuAnswerItem, ZhihuQuestionItem

try:
    import urlparse as parse
except:
    from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']
    # question的第一页answer的请求
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?" \
                       "include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2" \
                       "Creward_info%2Cis_collapsed%2Cannotation_action%2" \
                       "Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2" \
                       "Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2" \
                       "Ccan_comment%2Ccontent%2Ceditable_content%2" \
                       "Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2" \
                       "Ccreated_time%2Cupdated_time%2Creview_info%2" \
                       "Cquestion%2Cexcerpt%2Crelationship.is_authorized%2" \
                       "Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2" \
                       "Cupvoted_followees%3Bdata%5B%2A%5D.mark_infos%5B%2" \
                       "A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2" \
                       "Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&" \
                       "limit={1}&offset={2}&sort_by=default"

    user_agent_FireFox = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0'
    headers = {
        "Host": "www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": user_agent_FireFox
    }

    #   覆盖掉setting里面值
    custom_settings = {
        "DOWNLOAD_DELAY": 10,
        "COOKIES_ENABLED": True
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
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行处理
                request_url = match_obj.group(1)
                question_id = match_obj.group(2)

                # 6.c
                # 可以把这个yield看作深度优先的入口 往深度遍历
                yield Request(request_url,
                              headers=self.headers,
                              meta={"question_id": question_id},
                              callback=self.parse_question)
            else:
                # 6.d
                # 如果不是question页面 则进一步跟踪
                yield Request(url, headers=self.headers, callback=self.parse)


    # 6.c.①
    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item
        question_id = int(response.meta.get("question_id", ""))
        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        # item_loader.add_css("title", ".App-main h1.QuestionHeader-title::text")
        item_loader.add_xpath("title", "//*[@class='QuestionHeader-title']/text()")
        item_loader.add_css("content", ".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeaderActions button::text")
        item_loader.add_css("watch_num", ".NumberBoard-value::text")
        item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")

        question_item = item_loader.load_item()

        # 6.c.②
        yield Request(self.start_answer_url.format(question_id, 20, 0),
                      headers=self.headers,
                      callback=self.parse_answer)
        # 6.c.③
        yield question_item

    # 6.c.④
    def parse_answer(self, response):
        # 处理question的answer
        answer_json = json.loads(response.text)
        is_end = answer_json["paging"]["is_end"]
        next_url = answer_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in answer_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["parise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield Request(next_url, headers=self.headers, callback=self.parse_answer)