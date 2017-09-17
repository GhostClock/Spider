### 用Crawl模板 爬取拉勾网

##### 1.查scrapy genspider有哪些模板
    scrapy genspider --list
  要是不指名的话，默认是以basic模板
  
  `
  basic
  crawl
  csvfeed
  xmlfeed
  `
##### 2.用crawl模板生成默认代码
    scrapy genspider -t crawl lagou www.lagou.com
    
##### 3.创建main.py用于调试
    from scrapy.cmdline import execute
    import sys, os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))   # 设置工程目录
    execute(["scrapy", "crawl", "lagou"])
 
##### 4.在setting里面设置请求头
    DEFAULT_REQUEST_HEADERS = {
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en',
      'Host': 'www.lagou.com',
      'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36',
      'Referer': 'https://www.lagou.com/',
      'Cookie': ""
    }
    
##### 5.编写提取规则
    def parse_job(self, response):
    #   解析拉勾网的职位
    item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)

    item_loader.add_css("title", ".job-name::attr(title)")

    item_loader.add_value("url", response.url)

    item_loader.add_value("uil_object_id", get_md5_Value(response.url))

    salary = response.css(".job_request .salary::text").extract()
    salary = re.findall("(\d+)k-(\d+)k", salary[0])
    salary_min = salary[0][0]
    salary_max = salary[0][1]

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