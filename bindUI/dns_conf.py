#!/usr/bin/env python
# -*- coding:utf-8 -*-

# DNS解析线路，定义好的线路最好不要修改或删除
DNS_RESOLUTION_LINE = (
    ('0', '默认'),
    ('cn', '国内'),
    ('abroad', '国外'),
    ('101', '电信'),
    ('102', '联通'),
    ('103', '移动'),
    ('104', '教育网'),
)

# 负责响应 显性URL、隐性URL转发的主机名(域名)
URL_FORWARDER_DOMAIN = 'free.q.com'
