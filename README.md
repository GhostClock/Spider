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
    
    
    
    
##### 6.在items.py中格式化数据，并编写SQL语句
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
        
##### 7.数据入库
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
        
##### 8.settings里面打开ITEM_PIPELINES
    ITEM_PIPELINES = {
       # 'Spider.pipelines.SpiderPipeline': 300,
       'Spider.pipelines.MysqlTwistedPiplines': 1,
    }