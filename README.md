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