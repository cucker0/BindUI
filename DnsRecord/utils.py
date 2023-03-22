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
    'CAA': COMMON_FIELD,
    'URI': COMMON_FIELD,
}
# DNS记录的字段值中要求必须小写的字段列表
record_lower_field = ['zone', 'host', 'resp_person', 'primary_ns']
# DNS记录类型列表
record_type = ('A', 'CNAME', 'MX', 'TXT', 'NS', 'AAAA', 'SRV', 'PTR', 'SOA', 'CAA', 'URI',)

def check_ipv4(ip:str) -> bool:
    """ 查检IP是否为合法的 IPv4

    :param ip:
    :return:
    """
    try:
        if IPy.IP(ip).version() != 4:
            return False
    except Exception as e:
        return False

    addr = ip.strip().split('.')
    if len(addr) != 4:
        return False
    score = 0
    for i in range(len(addr)):
        try:
            if 0 <= int(addr[i]) <= 255:
                score += 1
        except Exception as e:
            return False

    if score == 4:
        return True

    return False


def record_data_filter(data):
    """ 多条 rr 数据过滤

    更新或创建 record 根据type过滤 data key,把非必要字段都留空,把type字段转为大写，CharField字段要求小写的转为小写
    :param data: 接收到 web 端的数据，格式：[{"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "comment":_comment, "zone":_zone_tag_name }]
        要更新或创建 的 record数据
    :return: 返回过滤后的data或业务处理异常消息
    """

    if type(data) != list:
        print(COMMON_MSG['data_type_error'])
        print('data structure like [{"type":_type, "host":_host}, {"type":_type, "host":_host}, ]')
        data = None
        return data
    for i in range(len(data)):
        if type(data[i]) != dict:
            continue
        if data[i]['type']:
            data[i]['type'] = data[i]['type'].upper()  # type字段转为大写
        if not (data[i]['type'] in record_type):  # type不在范围内的返回None
            continue
        # host为空时，设置默认值 @
        if not data[i]['host']:
            data[i]['host'] = '@'

        for k in data[i].keys():  # 去除用户提交data各值的左右空格
            if type(data[i][k]) == str:
                data[i][k] = data[i][k].strip()
        if data[i]['type'] in list(record_request_field.keys()):
            lower_set = set(data[i].keys()) & set(record_lower_field)
            for f in lower_set:  # CharField要求小写的转换成小写
                if data[i][f]:
                    data[i][f] = data[i][f].lower()
            not_request_set = set(record_key) - set(record_request_field[data[i]['type']])
            for key in not_request_set:  # # 不要求填写字段置为None
                data[i][key] = None
            if data[i]['type'] != 'MX':
                data[i]['mx_priority'] = None

            if data[i]['type'] == 'A':  # data字段过滤，要求IPv4
                if not check_ipv4(data[i]['data']):
                    print("%s 不是合法的IPv4地址。", data[i]['data'])
                    data[i] = None
            elif data[i]['type'] == 'AAAA':  # 要求IPv6
                try:
                    preip = IPy.IP(data[i]['data'])
                    if preip.version() == 6:
                        data[i]['data'] = preip.strNormal()
                    else:
                        data[i] = None
                except Exception as e:
                    data[i] = None
                    print(e)
            # elif data['type'] == 'CNAME' or (data['type'] == 'NS') or data['type'] == 'SOA' or data['type'] == 'PTR':
            elif data[i]['type'] in ('CNAME', 'NS', 'SOA', 'PTR'):
                # 要求为域名，如www.abc.com. 或 www.abc.com
                reg1 = "^([a-zA-Z0-9]+(-[a-z0-9]+)*\.)+[a-z]{1,}$"
                reg2 = "^([a-zA-Z0-9]+(-[a-z0-9]+)*\.)+[a-z]{1,}\.$"
                compile_data1 = re.compile(reg1)
                compile_data2 = re.compile(reg2)
                if compile_data1.match(data[i]['data']):
                    data[i]['data'] = "%s." % (data[i]['data'])
                elif compile_data2.match(data[i]['data']):
                    pass
                else:
                    data[i] = None

                if data[i]['type'] == 'SOA':
                    if not data[i]['resp_person'].endswith('.'):
                        data[i]['resp_person'] = "%s." % (data[i]['resp_person'])
                    if not data[i]['primary_ns'].endswith('.'):
                        data[i]['primary_ns'] = "%s." % (data[i]['primary_ns'])
            else:
                pass
    return data

def a_record_data_filter(rr:dict) -> bool:
    """ 单个 rr 数据过滤

    更新或创建 record 根据type过滤 data key，把非必要字段都留空,把type字段转为大写，CharField字段要求小写的转为小写
    :param rr: 格式：{"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "comment":_comment, "zone":_zone_tag_name }
    :return: 数据是否合格，True：合格，False: 不合格
    """

    if type(rr) != dict:
        print('data structure like {"type":_type, "host":_host}, {"type":_type, "host":_host}')
        return False

    if type(rr) != dict:
        print(COMMON_MSG['data_type_error'])
        return False
    if rr['type']:
        rr['type'] = rr['type'].upper()  # type字段转为大写
    if not (rr['type'] in record_type):  # type不在范围内的返回None
        print("rr type[%s] is not in the define range." % rr['type'])
        return False
    # host为空时，设置默认值 @
    if not rr['host']:
        rr['host'] = '@'

    for k in list(rr.keys()):  # 去除用户提交data各值的左右空格
        if type(rr[k]) == str:
            rr[k] = rr[k].strip()
    if rr['type'] in list(record_request_field.keys()):
        lower_set = set(rr.keys()) & set(record_lower_field)
        for f in lower_set:  # CharField要求小写的转换成小写
            if rr[f]:
                rr[f] = rr[f].lower()
        not_request_set = set(record_key) - set(record_request_field[rr['type']])
        for key in not_request_set:  # # 不要求填写字段置为None
            rr[key] = None
        if rr['type'] != 'MX':
            rr['mx_priority'] = None

        if rr['type'] == 'A':  # data字段过滤，要求IPv4
            if not check_ipv4(rr['data']):
                print("%s 不是合法的IPv4地址。" % rr['data'])
                return False
        elif rr['type'] == 'AAAA':  # 要求IPv6
            try:
                preip = IPy.IP(rr['data'])
                if preip.version() == 6:
                    # rr['data'] = preip.strNormal()
                    pass
                else:
                    return False
            except Exception as e:
                print(e)
                return False
        elif rr['type'] in ('CNAME', 'NS', 'SOA', 'PTR'):
            # 要求为域名，如www.abc.com. 或 www.abc.com
            reg1 = "^([a-zA-Z0-9]+(-[a-z0-9]+)*\.)+[a-z]{1,}$"
            reg2 = "^([a-zA-Z0-9]+(-[a-z0-9]+)*\.)+[a-z]{1,}\.$"
            compile_data1 = re.compile(reg1)
            compile_data2 = re.compile(reg2)
            if compile_data1.match(rr['data']):
                rr['data'] = "%s." % (rr['data'])
            elif compile_data2.match(rr['data']):
                pass
            else:
                return False

            if rr['type'] == 'SOA':
                if not rr['resp_person'].endswith('.'):
                    rr['resp_person'] = "%s." % (rr['resp_person'])
                if not rr['primary_ns'].endswith('.'):
                    rr['primary_ns'] = "%s." % (rr['primary_ns'])
        else:
            pass

    return True

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
