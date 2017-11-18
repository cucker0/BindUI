from django.shortcuts import render, redirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

COMMON_MSG = {'req_use_post':'use POST request method please.',
              'data_type_error':'data type is error!',
              }

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



def  MyPaginator(obj_set, page=1, perpage_num=5, pagiformart=[1, 2, 1]):
    """
    自定义分页器

    :param obj_set: 对象集
    :param page: 当前查看页页码（活动页）int
    :param perpage_num: 每页展示对象数量,int型
    :param pagiformart: 分页格式，左、中、右 显示个数， list
    :return: 分页后的子对象集,前端分页导航条html
    注意把 前端分页导航条html(pagination_html) 传到模板
    """

    # 上一页 1 2 ... 4 5 6 ... 9 10 下一页         #导航条示例
    L_NUM = pagiformart[0]       # 导航条左边显示个数
    M_NUM = pagiformart[1]//2 * 2 + 1     # 导航条中间显示个数，只能为大于1的奇数,如3、5、7 ...
    R_NUM = pagiformart[2]       # 导航条左边显示个数
    if type(page) == str:
        page = int(page)

    paginator = Paginator(obj_set, perpage_num)

    try:
        sub_obj_set = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sub_obj_set = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        sub_obj_set = paginator.page(paginator.num_pages)

    # 拼接前端的分页导航条html
    # 分成 上一页、中间页码、下一页 3个部分
    pagination_prev_element, pagination_middle_element, pagination_next_element = '', '', ''
    if sub_obj_set.has_previous():      # 上一页
        pagination_prev_element = '''
        <ul class="pagination">
            <li>
                <a href="#" aria-label="Previous"><span aria-hidden="true">&lt;</span></a>
            </li>
'''
    else:
        pagination_prev_element = '''
        <ul class="pagination">
            <li class="disabled">
                <a href="#" aria-label="Previous"><span aria-hidden="true">&lt;</span></a>
            </li>
'''

    if sub_obj_set.has_next():  # 下一页
        pagination_next_element = '''
            <li>
                <a href="#" aria-label="Next"><span aria-hidden="true">&gt;</span></a>
            </li>
        </ul>
'''
    else:
        pagination_next_element = '''
            <li class="disabled">
                <a href="#" aria-label="Next"><span aria-hidden="true">&gt;</span></a>
            </li>
        </ul>
'''


    #-- 导航条数字部分 --#
    if paginator.num_pages <= (L_NUM + M_NUM + R_NUM):      #### 情况A：导航条数字部分无省略标情况
        for page_num in paginator.page_range:
            if page_num == page:
                pagination_middle_element += \
'''
            <li class="active">
                <a href="#">%s</a>
            </li>
''' %(page_num)
            else:
                pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)

    if paginator.num_pages > (L_NUM + M_NUM + R_NUM):  #### 情况B：导航条数字部分有省略标情况
        if page <= (L_NUM + M_NUM//2 + 1):       ### 情况B.1 活动页位于导航条数字左边
            for i in range(L_NUM + M_NUM):  # 情况B.1 导航条数字左边 + 中间
                page_num = i + 1
                if page_num == page:
                    pagination_middle_element += \
'''
            <li class="active">
                <a href="#">%s</a>
            </li>
''' %(page_num)
                else:
                    pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)

            # 情况B.1 导航条数字右边
            pagination_middle_element += \
'''
            <li class="next-pagination-ellipsis">
            <a href="#">...</a>
            </li>
'''
            for i in range(R_NUM):
                page_num = paginator.num_pages - R_NUM + 1 + i
                pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)

        elif page > (L_NUM + M_NUM//2 + 1) and page <= (paginator.num_pages - R_NUM - (M_NUM//2 + 1) ):     ### 情况B.2：活动页位于导航条数字中间
            for i in range(L_NUM):      #情况B.2 导航条数字左边部分
                page_num = i + 1
                pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)

            # 情况B.2 左省略标
            pagination_middle_element += \
'''
            <li class="next-pagination-ellipsis">
            <a href="#">...</a>
            </li>
'''
            num = M_NUM // 2
            for i in range(num):     #情况B.2 导航条数字中间
                page_num = page - num + i
                pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)
            pagination_middle_element += \
'''
            <li class="active">
                <a href="#">%s</a>
            </li>
''' %(page)
            for i in range(num):     #情况B.2 导航条数字中间
                page_num = page + 1 + i
                pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)

            # 情况B.2 右省略标
            pagination_middle_element += \
'''
            <li class="next-pagination-ellipsis">
            <a href="#">...</a>
            </li>
'''
            # 情况B.2 导航条数字右边
            for i in range(R_NUM):
                page_num = paginator.num_pages - R_NUM + 1 + i
                pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)

        elif page > (paginator.num_pages - R_NUM - (M_NUM//2+1) ):      # 情况B.3：活动页位于导航条数字右边
            for i in range(L_NUM):      #情况B.3 导航条数字左边部分
                page_num = i + 1
                pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)

            # 情况B.3 左省略标
            pagination_middle_element += \
'''
            <li class="next-pagination-ellipsis">
            <a href="#">...</a>
            </li>
'''
            page_num_right_origin = paginator.num_pages - M_NUM - R_NUM + 1
            for i in range(M_NUM + R_NUM):      #情况B.3 导航条数字 中间 + 右边 部分
                page_num = page_num_right_origin + i
                if page_num == page:
                    pagination_middle_element += \
'''
            <li class="active">
                <a href="#">%s</a>
            </li>
''' %(page_num)
                else:
                    pagination_middle_element += \
'''
            <li>
                <a href="#">%s</a>
            </li>
''' %(page_num)

    #-- end 导航条数字部分 --#

    pagination_html = \
'''<!-- 分页导航条 -->
<div class="col-xs-12">
    <nav aria-label="pagination-1">
    %s
    %s
    %s
    </nav>
</div>
<!-- end 分页导航条 -->
''' %(pagination_prev_element, pagination_middle_element, pagination_next_element)
    # end 拼接前端的分页导航条html ##

    return sub_obj_set, pagination_html

def record_list(req, domain_id):
    """
    域名解析展示列表
    :param req:
    :return:
    """

    if req.method == "POST":
        data = json.loads(req.POST.get('data'))
        if 'page' in data.keys():
            page = int(data['page'])
        else:
            page = 1
    else:
        page = 1
    zone_tag_obj = models.ZoneTag.objects.get(id=domain_id)
    record_obj_list = zone_tag_obj.ZoneTag_Record.all()

    record_obj_perpage_list, pagination_html  = MyPaginator(record_obj_list, page)
    return render(req, 'bind/record_list.html',
                  {'record_obj_list': record_obj_perpage_list,
                   'pagination_html': pagination_html,
                   'zone_tag_obj': zone_tag_obj,
                   'DNS_RESOLUTION_LINE': dns_conf.DNS_RESOLUTION_LINE
                   })

def rlist_page(req):
    """
    DNS记录 page翻页
    :param req:
    :return:
    """
    if req.method == 'POST':
        data = json.loads(req.POST.get('data'))
        zone_tag_obj = models.ZoneTag.objects.get(zone_name=data['zone'])
        record_obj_list = zone_tag_obj.ZoneTag_Record.all()
        record_obj_perpage_list, pagination_html  = MyPaginator(record_obj_list, data['page'])
    return render(req, 'bind/tmp/domain_record_table_tmp.html',
                  {'record_obj_list': record_obj_perpage_list,
                   'pagination_html': pagination_html,
                   'zone_tag_obj': zone_tag_obj,
                   'DNS_RESOLUTION_LINE': dns_conf.DNS_RESOLUTION_LINE
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
        return HttpResponse(COMMON_MSG['req_use_post'])



record_key = ['zone', 'host', 'type', 'data', 'ttl', 'mx_priority', 'refresh', 'retry', 'expire', 'minimum', 'serial', 'resp_person', 'primary_ns', 'comment',]
record_request_field = {
    'A':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'CNAME':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'MX':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'mx_priority', 'comment'],
    'TXT':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'NS':['zone', 'host', 'type', 'data', 'resolution_line', 'comment'],
    'AAAA':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'SRV':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
    'PTR':['zone', 'host', 'type', 'data', 'ttl', 'resolution_line', 'comment'],
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
            for i in diff_set:
                data[i] = None
            return data
        else:
            return COMMON_MSG['data_type_error']
    else:
        return "update or create record data type is not dict"



def record_del(req):
    """

    :param req:
    :return:
    """
    if req.method == 'POST':
        msg = {'status': 500}
        data = json.loads(req.POST.get('data'))
        success_count = 0
        total_count = len(data)
        for i in data:
            try:
                record_obj = models.Record.objects.get(id=i)
                record_obj.delete()
                success_count += 1
            except Exception as e:
                print(e)
        if success_count == total_count:
            msg['status'] = 200
            msg['total_count'] = total_count
            msg['success_count'] = success_count
        return HttpResponse(json.dumps(msg))
    else:
        return HttpResponse(COMMON_MSG['req_use_post'])


def record_mod(req):
    """
    修改DNS记录状态
    :param req:
    :return:
    """
    msg = {'status': 500}
    type = req.GET.get('type')      #  <==>  type = req.GET['type'] ,两种用法都可以
    if req.method == 'POST':
        data = json.loads(req.POST.get('data'))
        if type == 'status':        # 修改staus
            if data['id_list']:
                record_obj_list = models.Record.objects.filter(id__in=data['id_list'])
            try:
                if data['action'] == '_turnOff':
                    record_obj_list.update(status='off')
                else:
                    record_obj_list.update(status='on')
                msg['status'] = 200
            except Exception as e:
                print(e)

        elif type == 'main':      # 修改DNS记录除staus外的项
            try:
                record_obj_set = models.Record.objects.filter(id=data['id'])

                del(data['id'])     # data.pop('id') print key
                # record_data_filter(data)
                zone_tag_obj = models.ZoneTag.objects.get(zone_name=data['zone'])
                data['zone_tag'] = zone_tag_obj
                record_obj_set.update(**data)
                msg['status'] = 200
            except Exception as e:
                print(e)

        return HttpResponse(json.dumps(msg))
    else:
        return HttpResponse(COMMON_MSG['req_use_post'])
