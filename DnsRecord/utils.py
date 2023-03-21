#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime, IPy, re
from bindUI import dns_conf


"""
msg = {'status': code}
status 响应状态
    200：成功
    500：失败
"""

COMMON_MSG = {'req_use_post':'use POST request method please.',
              'data_type_error':'data type is error!',
              }
# dns记录的字段列表
record_key = ['zone', 'host', 'type', 'data', 'ttl', 'mx_priority', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'resp_person', 'primary_ns', 'comment',]
# 多个DNS记录类型通用的必填字段列表 
COMMON_FIELD = ['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment']
# 每个DNS记录类型必填的字段
record_request_field = {
    'A': COMMON_FIELD,
    'CNAME': COMMON_FIELD,
    'MX': ['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'mx_priority', 'comment'],
    'TXT': COMMON_FIELD,
    'NS': COMMON_FIELD,
    'AAAA': COMMON_FIELD,
    'SRV': COMMON_FIELD,
    'PTR': COMMON_FIELD,
    'SOA': ['zone', 'host', 'type', 'data', 'ttl', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'resp_person', 'primary_ns', 'comment'],
}
# DNS记录的字段值中要求必须小写的字段列表
record_lower_field = ['zone', 'host', 'data', 'resp_person', 'primary_ns']
# DNS记录类型列表
record_type = ('A', 'CNAME', 'MX', 'TXT', 'NS', 'AAAA', 'SRV', 'PTR', 'SOA', 'CAA', 'EXPLICIT_URL', 'IMPLICIT_URL')

def record_data_filter(data):
    """ 数据过滤
    
    更新或创建 record 根据type过滤 data key,把非必要字段都留空,把type字段转为大写，CharField字段要求小写的转为小写
    :param data: 接收到 web 端的数据，格式：[{"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "comment":_comment, "zone":_zone_tag_name }]
        要更新或创建 的 record数据
    :return: 返回过滤后的data或业务处理异常消息
    """

    if type(data) == dict:
        if not (data['type'] in record_type): # type不在范围内的返回None
            data = None
            return data

        # host为空时，设置默认值 @
        if not data['host']:
            data['host'] = '@'

        if data['type']:
            data['type'] = data['type'].upper()     # type字段转为大写

        for k in data.keys():       # 去除用户提交data各值的左右空格
            if type(data[k]) == str:
                data[k] = data[k].strip()
        if data['type'] in record_request_field.keys():
            lower_set = set(data.keys()) & set(record_lower_field)
            for f in lower_set:        # CharField要求小写的转换成小写
                if data[f]:
                    data[f] = data[f].lower()

            not_request_set = set(record_key) - set(record_request_field[data['type']])
            for i in not_request_set:       # # 不要求填写字段置为None
                data[i] = None

            if data['type'] != 'MX':
                data['mx_priority'] = None

            if data['type'] == 'A':     # data字段过滤，要求IPv4
                try:
                    preip = IPy.IP(data['data'])
                    if preip.version() == 4:
                        data['data'] = preip.strNormal()
                    else:
                        data = None
                except Exception as e:
                    data = None
                    print(e)
            elif data['type'] == 'AAAA':        # 要求IPv6
                try:
                    preip = IPy.IP(data['data'])
                    if preip.version() == 6:
                        data['data'] = preip.strNormal()
                    else:
                        data = None
                except Exception as e:
                    data = None
                    print(e)
            # elif data['type'] == 'CNAME' or (data['type'] == 'NS') or data['type'] == 'SOA' or data['type'] == 'PTR':
            elif data['type'] in ('CNAME', 'NS', 'SOA', 'PTR'):
                # 要求为域名，如www.abc.com. 或 www.abc.com
                reg1 = "^([a-zA-Z0-9]+(-[a-z0-9]+)*\.)+[a-z]{1,}$"
                reg2 = "^([a-zA-Z0-9]+(-[a-z0-9]+)*\.)+[a-z]{1,}\.$"
                compile_data1 = re.compile(reg1)
                compile_data2 = re.compile(reg2)
                if compile_data1.match(data['data']):
                    data['data'] = "%s." %(data['data'])
                elif compile_data2.match(data['data']):
                    pass
                else:
                    data =None

                if data['type'] == 'SOA':
                    if not data['resp_person'].endswith('.'):
                        data['resp_person'] = "%s." %(data['resp_person'])
                    if not data['primary_ns'].endswith('.'):
                        data['primary_ns'] = "%s." %(data['primary_ns'])
            # elif data['type'] == 'IMPLICIT_URL':
            #     data['basic'] = 200
            else:
                pass

            return data
        else:
            return COMMON_MSG['data_type_error']
    else:
        return "update or create record data type is not dict"


def serial(num=0):
    """ 10位序列号的生成与修改
    
    用于SOA记录的serial字段，要求长度为10位的数字
    格式：YYYYxxxxxx
    :param num:
    :return:
    """
    now = datetime.datetime.now()
    YYYY = now.year
    # 生成10位序列号，初始值为 YYYY000001，也是该年最小的一个序号
    num_str = "%s%s" % (str(YYYY), '1'.zfill(6))
    num_gen = int(num_str)
    if num == 0:
        return num_gen
    else:
        if len(str(num)) < 10:  # 原来设置的serial值小于10位的，直接使用标准的10位serial值
            return num_gen
        elif len(str(num)) > 10:  # serial值大于10位的异常情况，取其最左边的10位
            num = str(num)[:10]

        # 从serial字段中提取年份
        year_of_serial = str(num)[:4]
        year_of_serial = int(year_of_serial)
        # 如果提供过来的serial值(即num)里的年份比当前的年份小，则把serial更新为当前年份的一个最小序号(新生成的序号)
        if year_of_serial < YYYY:
            return num_gen
        else:  # year_of_serial >= YYYY情况
            # 目前的serial值比该年最小的初始serial值还小的情况，直接更新serial值为num_gen
            if int(num) < num_gen:
                return num_gen
            # 正常情况下，序列号递增
            num = int(num) + 1

    return num

def get_url_forwarder_domain() -> str:
    """ 获取 显性URL、隐性URL转发的主机名(域名)

    :return:
    """
    return dns_conf.URL_FORWARDER_DOMAIN
