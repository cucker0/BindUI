from django.shortcuts import render, redirect, HttpResponse
from . import models

import sys, os
BASIC_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASIC_DIR)
from bindUI import dns_conf
import json

# Create your views here.

"""
msg = {'status': code}
code 值含义
    200：成功
    500：失败
"""

def root(req):
    return redirect('/')

def index(req):
    """
    首页
    :param req:
    :return:
    """
    return render(req, 'bind/index.html')

def domain_list(req):
    """
    dashboard, domain list
    :param req:
    :return:
    """
    zone_obj_list = models.ZoneTag.objects.all()
    return render(req, 'bind/domain_list.html', {'zone_obj_list': zone_obj_list})

def domain_add(req):
    """

    :param req:
    :return:
    """
    pass


def domain_resolution_list(req):
    """
    dashboard, domain list
    :param req:
    :return:
    """
    zone_obj_list = models.ZoneTag.objects.all()
    return render(req, 'bind/domain_resolution_list.html', {'zone_obj_list': zone_obj_list})


def record_list(req, domain_id):
    """
    域名解析展示列表
    :param req:
    :return:
    """
    zone_tag_obj = models.ZoneTag.objects.get(id=domain_id)
    record_obj_list = zone_tag_obj.ZoneTag_Record.all()
    return render(req, 'bind/record_list.html', {'record_obj_list': record_obj_list,
                                                 'zone_tag_obj': zone_tag_obj,
                                                 'DNS_RESOLUTION_LINE':dns_conf.DNS_RESOLUTION_LINE
                                                 })

def record_add(req):
    """
    添加解析记录
    :param req:
    :return:
    """
    if req.method == 'POST':
        data = req.POST.get('data')
        msg = {'status': 500}
        try:
            data = json.loads(data)
            # data = record_data_filter(data)
            record_data_filter(data)        # 传递参数为字典时是以指针形式传递的
            zone_tag_obj = models.ZoneTag.objects.get(zone_name=data['zone'])
            data['zone_tag'] = zone_tag_obj
            models.Record.objects.update_or_create(**data)
            msg['status'] = 200
        except Exception as e:
            print(e)
        return HttpResponse(json.dumps(msg))
    else:
        return HttpResponse('use POST request method please.')



record_key = ['zone', 'host', 'type', 'data', 'ttl', 'mx_priority', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'resp_person', 'primary_ns', 'comment',]
record_request_field = {
    'A':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line'],
    'CNAME':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line'],
    'MX':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'mx_priority'],
    'TXT':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line'],
    'NS':['zone', 'host', 'type', 'data', 'resolution_line'],
    'AAAA':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line'],
    'SRV':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line'],
    'PTR':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line'],
    'SOA':['zone', 'host', 'type', 'data', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'resp_person', 'primary_ns'],
}

def record_data_filter(data):
    """
    更新或创建 record 根据type过滤 data key,把非必要字段都留空
    :param data: 要更新或创建 的 record数据，字典形式
    :return:
    """
    if type(data) == dict:
        if data['type'] in record_request_field.keys():
            diff_set = set(record_key) - set(record_request_field[data['type']])
            print(diff_set)
            for i in diff_set:
                data[i] = None
            return data
        else:
            return "data type error"
    else:
        return "update or create record data type is not dict"



