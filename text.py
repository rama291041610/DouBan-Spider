#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from langconv import *
import re

chstd = re.compile(u'[\u4e00-\u9fa5]+')


def cht_to_chs(content):
    '''繁体->简体'''
    content = Converter('zh-hans') .convert(content)
    content.encode('utf-8')
    return content


def is_chinese(content):
    '''判断是否包含汉字'''
    content = cht_to_chs(content)
    cmp = chstd.search(content)
    if cmp:
        return True
    else:
        return False


def delete_black(content):
    return content.replace('\n', '').replace('\r', '').replace('\t', '')
