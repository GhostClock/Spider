# -*- coding=utf-8 -*-
__author__ = 'ghostclock'

from scrapy.cmdline import execute

import sys, os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))   # 设置工程目录

execute(["scrapy", "crawl", "lagou"])