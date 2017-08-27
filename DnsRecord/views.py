from django.shortcuts import render, redirect
from . import models

# Create your views here.

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

    return render(req, 'bind/record_list.html', {'record_obj_list': record_obj_list, 'zone_tag_obj':zone_tag_obj})

def record_add(req):
    """
    添加解析记录
    :param req:
    :return:
    """
    pass



