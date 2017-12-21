#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime

def serial(num=0):
    """
    10位序列号生成与修改
    :param num:
    :return:
    """
    now = datetime.datetime.now()
    YYYY = now.year
    if num == 0:    # 生成10位序列号
        num_str = "%s%s" %(str(YYYY), '1'.zfill(6))
        num = int(num_str)
    else:       # 序列号递增
        if len(str(num)) <= 10:
            num = int(num)
            num +=1
        else:
            num = str(num)[:10]
            num = int(num)
            num += 1
    return num
