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
##### 2.生成模板
    scrapy genspider -t lagou www.lagou.com

