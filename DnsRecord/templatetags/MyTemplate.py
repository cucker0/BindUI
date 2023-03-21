#!/usr/bin/env python
# -*- coding:utf-8 -*-

## 自定义模板

from django import template
from django.utils.html import format_html

import sys, os
BASIC_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASIC_DIR)
from bindUI import dns_conf
import datetime

register = template.Library()

@register.simple_tag
def truncate_url(img_url):
    """
    截断图片URL
    如 uploads/user_image/01.png        ==>  /user_image/01.png
    :param img_url: 图片路径
    :return: 截断处理后的url
    """
    if img_url:
        img_url = str(img_url)
        url = img_url.split('/', maxsplit=1)[-1]
    else:
        url = 'system/head_img_00.jpg'
    return url

@register.filter
def is_reverse_resulution_domain(domain_name):
    """
    是否为反向解析域
    :param domain_name: 域名
    :return: True/False
    """
    if domain_name.endswith('in-addr.arpa'):
        return True
    else:
        return False


@register.simple_tag
def val_none_to_blank(data, default='-'):
    """
    模板中把 None值转到成 指定值
    :return: 过滤处理后的data
    """
    if (data is None) or (data == ''):
        data = default
    return data

@register.simple_tag
def ttl_convert(ttl, default='-'):
    """
    ttl值 秒转到成 分钟/小时
    :param ttl:
    :return: ttl转换后值
    """
    ttl_convert_list = {
        60:'1分钟',
        600:'10分钟',
        1800:'30分钟',
        3600:'1小时',
        43200:'12小时',
        86400:'24小时',
    }
    if ttl is None or (ttl == '') :
        ttl = default
    elif ttl in ttl_convert_list.keys():
        ttl = ttl_convert_list[ttl]
    return ttl


def tuple_to_dic(tup):
    """
    把 DNS_RESOLUTION_LINE = (
    ('0', '默认'),
    ('cn', '国内'),
    ('abroad', '国外'),
    ('101', '电信'),
    ('102', '联通'),
    ('103', '移动'),
    ('104', '教育网'),
)
    转换成字典  {'0':'默认', 'cn':'国内'}
    :param tup: 元组数据
    :return: 元组数据转换后的字典(dict)
    """
    dic = {}
    for i in tup:
        dic[i[0]] = i[1]
    return dic


dns_resolution_line_dic = tuple_to_dic(dns_conf.DNS_RESOLUTION_LINE)  # 解析线路字典

@register.simple_tag
def dns_resolution_line_fileter(data):
    """
     从数据库获取的解析线路值转换成 相应的线路名 ('101', '电信')
    :param data: 数据库获取的解析线路值
    :return: 解析线路名（str）
    """
    if data in dns_resolution_line_dic:
        line_name = dns_resolution_line_dic[data]
    else:
        line_name = '未知'
    return line_name

@register.simple_tag
def status_convert(status):
    """
    根据status值显示相应的操作按钮，
    如status为on时,记录状态操作按钮为暂停，反之为开启
    :param status:记录status值
    :return: status值对应的状态操作按钮
    """
    action = '开启'
    if status  == 'on':
        action = '暂停'
    return action

@register.simple_tag
def get_year():
    """
    获取当年年份
    :return: 当年年份
    """
    now = datetime.datetime.now()
    YYYY = now.year
    return YYYY

@register.simple_tag
def rr_type_convert(rr_type:str, basic:int) ->str:
    """ 对 rr 的 type 进行转换

    :param rr_type: rr 的类型
    :param basic: rr 的 basic code
    :return:
    """
    if rr_type == 'TXT':
        if basic in dns_conf.EXPLICIT_URL_BASIC_SET:
            return '显性URL'
        elif basic in dns_conf.IMPLICIT_URL_SET:
            return '隐性URL'

    return rr_type
