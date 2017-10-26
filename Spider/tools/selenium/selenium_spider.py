# -*- coding=utf-8 -*-
__author__ = 'ghostclock'
"""
用slenium来模拟知乎
"""
from selenium import webdriver
from scrapy.selector import Selector

browser = webdriver.Chrome(executable_path='chromedriver.exe')
browser.get('https://www.zhihu.com/#signin')

account = browser.find_element_by_css_selector('.view.view-signin input[name="account"]').send_keys('youAccount')
browser.find_element_by_css_selector('.view-signin input[name="password"]').send_keys('youPassword')
browser.find_element_by_css_selector('view-signin button.sign-button')
browser.quit()
pass