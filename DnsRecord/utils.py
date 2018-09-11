#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime, IPy, re


"""
msg = {'status': code}
code 值含义
    200：成功
    500：失败
"""

COMMON_MSG = {'req_use_post':'use POST request method please.',
              'data_type_error':'data type is error!',
              }

record_key = ['zone', 'host', 'type', 'data', 'ttl', 'mx_priority', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'resp_person', 'primary_ns', 'comment',]
record_request_field = {
    'A':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'CNAME':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'MX':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'mx_priority', 'comment'],
    'TXT':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'NS':['zone', 'host', 'type', 'data', 'ttl','resolution_line', 'comment'],
    'AAAA':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'SRV':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'PTR':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'SOA':['zone', 'host', 'type', 'data', 'ttl', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'resp_person', 'primary_ns', 'comment'],
}

record_lower_field = ['zone', 'host', 'data', 'resp_person', 'primary_ns']

record_type = ('A', 'CNAME', 'MX', 'TXT', 'NS', 'AAAA', 'SRV', 'PTR', 'SOA')

def record_data_filter(data):
    """
    数据过滤
    更新或创建 record 根据type过滤 data key,把非必要字段都留空,把type字段转为大写，CharField字段要求小写的转为小写
    :param data: 要更新或创建 的 record数据，字典形式
    :return:
    """

    if type(data) == dict:
        if not (data['type'] in record_type): # type不在范围内的返回None
            data = None
            return data

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

            if data['type'] == 'A':     # data字段过滤，要求IP4
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
            elif data['type'] == 'CNAME' or (data['type'] == 'NS') or data['type'] == 'SOA' or data['type'] == 'PTR':    # 要求为域名，如www.abc.com.
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
            else:
                pass

            return data
        else:
            return COMMON_MSG['data_type_error']
    else:
        return "update or create record data type is not dict"


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
