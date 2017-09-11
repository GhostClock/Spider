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
