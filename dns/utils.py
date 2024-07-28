#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime, IPy, re
import math
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
record_key = ['zone', 'host', 'type', 'data', 'ttl', 'mx_priority', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'mail', 'primary_ns', 'comment',]
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
    'SOA': ['zone', 'host', 'type', 'data', 'ttl', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'mail', 'primary_ns', 'comment'],
    'CAA': COMMON_FIELD,
    'URI': COMMON_FIELD,
}
# DNS记录的字段值中要求必须小写的字段列表
record_lower_field = ['host', 'mail', 'primary_ns']
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


def records_data_filter(data):
    """ 多条 rr 数据过滤

    更新或创建 record 根据type过滤 data key,把非必要字段都留空,把type字段转为大写，CharField字段要求小写的转为小写
    :param data: list[dict]
        接收到 web 端的数据，
        格式：[{"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "comment":_comment, "zone":_zone_name }]
        要更新 或 创建 的多条 record 数据
    :return: list[dict] or any
        返回过滤后的data或业务处理异常消息
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
            elif data[i]['type'] == 'TXT':  # TXT 类型的 RR 的值超过 255 个字符时需要分割成多个字符串，使用 " " 连接分割的各个部分
                data[i]['data'] = split_txt(data[i]['data'])
            elif data[i]['type'] in ('CNAME', 'NS', 'SOA', 'PTR'):
                # 要求为域名，如www.abc.com. 或 www.abc.com
                data[i]['data'] = endwith_dot(data[i]['data'])

                if data[i]['type'] == 'SOA':
                    if not data[i]['mail'].endswith('.'):
                        data[i]['mail'] = "%s." % (data[i]['mail'])
                    if not data[i]['primary_ns'].endswith('.'):
                        data[i]['primary_ns'] = "%s." % (data[i]['primary_ns'])
            else:
                pass
    return data


def a_record_data_filter(rr: dict) -> bool:
    """ 单个 rr 数据过滤

    更新或创建 record 根据type过滤 data key，把非必要字段都留空,把type字段转为大写，CharField字段要求小写的转为小写
    :param rr: dict
        需要过滤的RR
        格式：{"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "comment":_comment, "zone": zone_obj }
    :return: bool
        数据是否合格，True：合格，False: 不合格
    """
    if type(rr) != dict:
        print(COMMON_MSG['data_type_error'])
        print('data structure like {"type":_type, "host":_host}, {"type":_type, "host":_host}')
        return False
    rr_keys = list(rr.keys())
    if 'type' in rr_keys:
        if rr['type']:
            rr['type'] = rr['type'].upper()  # type字段转为大写
        if not (rr['type'] in record_type):  # type不在范围内的返回None
            print("rr type[%s] is not in the define range." % rr['type'])
            return False
    # host为空时，设置默认值 @
    if 'host' in rr_keys and (not rr['host']):
        rr['host'] = '@'
    for k in rr_keys:  # 去除用户提交data各值的左右空格
        if type(rr[k]) == str:
            rr[k] = rr[k].strip()
    if 'type' in rr_keys and (rr['type'] in list(record_request_field.keys())):
        lower_set = set(rr.keys()) & set(record_lower_field)
        for f in lower_set:  # CharField要求小写的转换成小写
            if rr[f]:
                rr[f] = rr[f].lower()
        not_request_set = set(record_key) - set(record_request_field[rr['type']])
        for key in not_request_set:  # # 不要求填写字段置为None
            rr[key] = None
        if rr['type'] != 'MX':
            rr['mx_priority'] = None
        if rr['type'] == 'MX':
            if ('mx_priority' not in rr_keys) or (not rr['mx_priority']):
                rr['mx_priority'] = '10'
            if not check_ipv4(rr['data']) or IPy.IP(rr['data']).version() != 6:
                rr['data'] = endwith_dot(rr['data'])

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
        elif rr['type'] == 'TXT':  # TXT 类型的 RR 的值超过 255 个字符时需要分割成多个字符串，使用 " " 连接分割的各个部分
            rr['data'] = split_txt(rr['data'])
        elif rr['type'] in ('CNAME', 'NS', 'SOA', 'PTR'):
            # 要求为域名，如www.abc.com. 或 www.abc.com
            rr['data'] = endwith_dot(rr['data'])
            if rr['data'] == '':
                return False
            if rr['type'] == 'SOA':
                if not rr['mail'].endswith('.'):
                    rr['mail'] = "%s." % (rr['mail'])
                if '@' in rr['mail']:
                    rr['mail'] = rr['mail'].replace('@', '.')
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

def get_url_forwarder_fqdn() -> str:
    """ 获取 显性URL、隐性URL转发的主机名(完整域名/完全限定域名)

    :return:
    """
    return endwith_dot(dns_conf.URL_FORWARDER_DOMAIN)

def endwith_dot(fqdn:str) -> str:
    """ 使给定的字符串 以"."结尾

    :param fqdn:
    :return:
    """
    if not fqdn:
        return ''
    if fqdn == '':
        return ''
    if type(fqdn) != str:
        return ''

    if fqdn.endswith('.'):
        pass
    else:
        fqdn = f"%s." % (fqdn)

    return fqdn


def action2status(action: str) -> str:
    """ 操作 RR 状态的动作 转换为 RR 的 status 值

    :param action:
    :return:
    """
    if action == '_turnOff':
        return 'off'
    return 'on'


def split_txt(txt: str) -> str:
    """ 超过 255 个字符的文本分割为多个字符串，使用 " " 连接分割的各个部分

    :param txt: str
        需要进行处理的文本字符串
    :return: str
        处理后的文本。
        因为 bind-dlz 查询 RR 的 SQL 对于 TXT 类型的记录，在查询出来的值首尾两边添加了 `"`（请参考 BIND 的配置 关于 dlz SQL 部分），
        所以这里不需要在处理后的文本的首尾添加`"`

    因为 BIND 对于 TXT 记录的值最大限制为 255个字符，如果超过则需要分割为多个字符串。
    参考 https://kb.isc.org/docs/aa-00356

    3.1.3.  Multiple Strings in a Single DNS record

    As defined in [RFC1035] sections 3.3.14 and 3.3, a single text DNS record (either TXT or SPF RR types) can be composed of more than one string. If a published record contains multiple strings, then the record MUST be treated as if those strings are concatenated together without adding spaces.  For example:

           IN TXT "v=spf1 .... first" "second string..."

      MUST be treated as equivalent to

           IN TXT "v=spf1 .... firstsecond string..."

    SPF or TXT records containing multiple strings are useful in constructing records that would exceed the 255-byte maximum length of a string within a single TXT or SPF RR record.
    """
    if len(txt) <= 255:
        return txt

    # 对于修改更新 TXT 记录的情况
    if txt.find('" "') != -1:
        txt = txt.replace('" "', '')

    tmp_txt = []
    i = 0
    n = 255
    while i < math.ceil(len(txt) / n):
        start = i * n
        end = (1 + i) * n
        if end > len(txt):
            end = len(txt)
        tmp_txt.append(txt[start: end])
        i += 1
    return '" "'.join(tmp_txt)
