# -*- coding=utf-8 -*-
__author__ = 'ghostclock'

from hashlib import md5
import re


def get_md5_Value(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = md5()
    m.update(url)
    return m.hexdigest()

def extract_num(text):
    # 从字符串中提取数字
    match_re = re.match(r".*?(\d+).*", text)

    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums