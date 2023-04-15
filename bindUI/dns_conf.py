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

# 负责响应 显性URL、隐性URL转发的主机名(域名)，使用FQDN A 记录，建议以 "." 结尾
URL_FORWARDER_DOMAIN = 'free.zz.com.'

# 需要在 WEB 端显示的 记录的 basic
BASIC_SET2SHOW = (0, 200, 301, 302)

# 显性URL basic code 集合
EXPLICIT_URL_BASIC_SET = (301, 302)

# 隐性URL basic code 集合
IMPLICIT_URL_SET = (200, )

# 显性URL、隐性URL basic code 集合
URL_FORWARDER_BASIC_SET = (200, 301, 302)