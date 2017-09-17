# -*- coding=utf-8 -*-
__author__ = 'ghostclock'

from hashlib import md5


def get_md5_Value(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = md5()
    m.update(url)
    return m.hexdigest()
