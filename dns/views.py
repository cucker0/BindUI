from django.shortcuts import render, redirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from . import models
from django.db.models import Q
from django.utils import timezone
import xlrd, xlwt
from django.core import serializers
import sys, os

BASIC_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASIC_DIR)
from bindUI import dns_conf
import json
from .utils import serial, records_data_filter, COMMON_MSG, get_url_forwarder_fqdn, a_record_data_filter, action2status, \
    split_txt

# Create your views here.

"""
msg = {'status': code}
status 响应状态
    200：成功
    500：失败
"""

@login_required
def root(req):
    return redirect('/')

@login_required
def index(req):
    """
    首页
    :param req:
    :return:
    """
    zone_count = models.Zone.objects.all().count()
    return render(req, 'bind/index.html', {'zone_count': zone_count})

@login_required
def domain_list(req):
    """ 我的域名 页面

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
    zone_obj_list = models.Zone.objects.all().order_by('id')
    zone_obj_perpage_list, pagination_html = MyPaginator(zone_obj_list, page)
    return render(req, 'bind/domain_list.html', {
        'zone_obj_list': zone_obj_list,
        'pagination_html':pagination_html,
    })

@login_required
def domain_status_mod(req):
    """
    修改doamin状态值，即开启或停用doamin
    :param req:
    :return:
    """
    msg = {'status': 500}
    if req.method == 'POST':
        data = json.loads(req.POST.get('data'))
        if data['id_list']:
            # print(data['id_list'], type(data['id_list']))
            zone_set = models.Zone.objects.filter(id__in=data['id_list'])
        try:
            if data['action'] == '_turnOff':
                zone_set.update(status='off')
            else:
                zone_set.update(status='on')
            # 更新 update_time
            zone_set.update(update_time=timezone.now())
            msg['status'] = 200
        except Exception as e:
            print(e)
    return msg

@login_required
def domain_curd(req):
    """
    域名增改查删分类请求转发
    :param req:
    :return:
    """
    resp = ''
    _type = req.GET.get('type').strip()
    if _type == 'c':        # 新增domain
        resp = domain_add(req)
    elif _type == 'm':  # 修改 doamin 的主要属性
        resp = domain_main_mod(req)
    elif _type == 'ns':     # 添加、修改ns记录
        resp = domain_ns(req)
    elif _type == 'status':     # 修改domain状态
        resp = domain_status_mod(req)
    elif _type == 'd':      # 删除domain
        resp = domain_delete(req)
    return HttpResponse(json.dumps(resp))


def domain_delete(req):
    """
    删除domain域名
    :param req:
    :return:
    """
    msg = {'status': 500, 'msg':''}
    if req.method == "POST":
        data = json.loads(req.POST.get('data'))
        if data['id_list']:
            zone_set = models.Zone.objects.filter(id__in=data['id_list'])
            try:
                for zone_obj in zone_set:
                    record_set = zone_obj.record_set.all()
                    record_set.delete()     # 删除dns记录
                zone_set.delete()      # 删除zone
                msg['status'] = 200
            except Exception as e:
                print(e)

    return msg


def domain_add(req):
    """
    新增domain域名
    :param req:
    :return:
    """
    msg = {'status': 500, 'msg':''}
    try:
        # data 数据格式
        """
        __data = {
            rr: {
                data: _data,
                mail: _mail,
                refresh: _refresh,
                retry: _retry,
                expire: _expire,
                minimum: _minimum,
                primary_ns: _primary_ns,
                comment: _comment
            },
            zone_name: _zone_name
        }
        """
        data = json.loads(req.POST.get('data'))
    except Exception as e:
        print(e)
    rr_raw = data['rr']
    rr_raw['type'] = 'SOA'
    rr_raw['basic'] = 2       # 标识为不可重复的基础记录
    rr_raw['host'] = '@'
    rr_raw['ttl'] = 3600
    rr_raw['serial'] = serial()
    a_record_data_filter(rr_raw)

    zone_obj = models.Zone.objects.filter(zone_name=data['zone_name'].strip()).first()
    record_set = None

    if zone_obj:
        msg['msg'] += "zone:%s exist; " %(data['zone_name'])
        record_set = models.Record.objects.filter(Q(type='SOA') & Q(zone_id=zone_obj.id))
    else:
        zone_raw = {'zone_name': data['zone_name']}
        try:
            if rr_raw['comment']:
                zone_raw['comment'] = rr_raw['comment']
        except KeyError:
            zone_raw['comment'] = None
        # 新建zone
        zone_obj = models.Zone.objects.create(**zone_raw)

    if record_set:
        msg['msg'] += "record SOA: %s exist!; " %(record_set.first().zone.zone_name)
    else:
        try:
            rr_raw['zone_id'] = zone_obj.id
            models.Record.objects.create(**rr_raw)
            msg['status'] = 200
            msg['msg'] = "%s create success." %(data['zone_name'])
        except Exception as e:
            print(e)
    return msg


def domain_main_mod(req):
    """ 修改 doamin 的主要属性（除了 status），就是更新一条 SOA 记录

    :param req:
    :return:
    """
    msg = {'status': 500}
    if req.method == 'POST':
        # data 格式
        """
        __data = {
            rr: {
                data: _data,
                mail: _mail,
                refresh: _refresh,
                retry: _retry,
                expire: _expire,
                minimum: _minimum,
                primary_ns: _primary_ns,
                comment: _comment
            },
            zone_id: GetCheckedDomainId()
        }
        """
        data: dict = json.loads(req.POST.get('data'))
        if type(data) != dict:
            return HttpResponse(COMMON_MSG['req_use_post'])

        try:
            record_obj_set = models.Record.objects.filter(
                Q(type='SOA') & Q(host='@') & Q(basic=2) & Q(zone_id=int(data['zone_id']))
            )
            if not record_obj_set:
                return msg
            rr_raw = data['rr']
            rr_raw['host'] = '@'
            rr_raw['type'] = 'SOA'
            rr_raw['serial'] = serial(record_obj_set.get().serial)
            rr_raw['update_time'] = timezone.now()
            a_record_data_filter(rr_raw)
            # 更新 record_obj_set
            record_obj_set.update(**rr_raw)
            # 更新 zone
            zone_obj = models.Zone.objects.get(id=int(data['zone_id']))
            zone_obj.update_time = record_obj_set.first().update_time
            zone_obj.comment = record_obj_set.first().comment
            zone_obj.save()

            msg['status'] = 200
        except Exception as e:
            print(e)

        return msg
    else:
        return COMMON_MSG['req_use_post']

def domain_ns(req):
    """
    domain NS记录创建、修改
    :param req:
    :return:
    """
    msg = {'status': 500, 'msg':''}
    if req.method != 'POST':
        return COMMON_MSG['req_use_post']
    try:
        data = json.loads(req.POST.get('data'))
        zone_id = int(data['zone_id'])
        ns_submit_set = set(data['ns_list'])        # 提交更新的domain NS集合
        zone_obj = models.Zone.objects.get(id=zone_id)
        if zone_obj:        # zone必须存在
            ns_obj_set = models.Record.objects.filter(Q(host='@') & Q(type='NS') & Q(zone_id=zone_id))
            ns_data_set = set()
            for i in ns_obj_set:
                ns_data_set.add(i.data)        # 数据库中已经存在domain NS集合
            ns_toadd_set = ns_submit_set - ns_data_set      # 需要创建的domain NS data字段集合
            ns_todelete_set = ns_data_set - ns_submit_set   # 需要删除的domian NS data字段集合
            for i in ns_toadd_set:
                ns_instance = {'host':'@', 'type':'NS', 'data':i.strip(), 'ttl':10800, 'basic':2, 'zone':zone_obj }
                a_record_data_filter(ns_instance)
                models.Record.objects.update_or_create(**ns_instance)
                msg['msg'] += "domain ns:%s create success; " %(i.strip())

            ns_todele_obj_set = models.Record.objects.filter(data__in=ns_todelete_set)
            ns_todele_obj_set.delete()
            for i in ns_toadd_set:
                msg['msg'] += "domain ns:%s delete success; " %(i.strip())

            # 更新 update_time
            # models.Zone.objects.filter(id=zone_id).update(update_time=timezone.now())
            zone_obj.update_time = timezone.now()
            zone_obj.save()
        msg['status'] = 200
    except Exception as e:
        print(e)

    return msg

@login_required
def domain_resolution_list(req):
    """
    dashboard, domain list
    :param req:
    :return:
    """
    zone_obj_list = models.Zone.objects.all().order_by('id')
    zone_obj_perpage_list, pagination_html  = MyPaginator(zone_obj_list, 1, 10)
    return render(req, 'bind/domain_resolution_list.html',
                  {'zone_obj_list': zone_obj_perpage_list,
                    'pagination_html':pagination_html,
                   })

@login_required
def domain_man(req, zone_id, optype):
    """
    域名管理
    :param req:
    :return:
    """
    zone_id = int(zone_id)
    zone_obj = models.Zone.objects.get(id=zone_id)
    ns_set = models.Record.objects.filter(Q(type='NS') & Q(basic=2) & Q(zone=zone_obj))
    return render(req, 'bind/domain_manager.html', {'zone_obj':zone_obj, 'ns_set': ns_set})

@login_required
def get_domain_by_id(req, zone_id):
    """ 通过域名id查询域名信息，即该域名的 SOA 记录

    rr_list_json 是一个 json 字符串，对象的数据格式
    '''
    [
        {
            "model": "dns.record",
            "pk": 115,
            "fields": {"host": "@", "type": "SOA", "data": "dns.z.cn.", "ttl": 3600, "mx_priority": null,
                 "refresh": 900, "retry": 900, "expire": 2592000, "minimum": 600, "serial": 2023000001,
                 "mail": "admin.qq.com.", "primary_ns": ".", "status": "on",
                 "create_time": "2023-04-08T04:20:01.930Z", "update_time": "2023-04-08T04:20:01.930Z", "comment": "",
                 "resolution_line": "0", "zone": 5, "basic": 2, "associate_rr_id": null
            }
        }
    ]
    '''

    :param req:
    :param domain_id: 域名id，类型为 int。
    :return: 单个域名信息（json类型）
    """
    zone_id = int(zone_id)
    zone_obj = models.Zone.objects.get(id=zone_id)
    rr_set = models.Record.objects.filter(Q(type='SOA') & Q(host='@') & Q(basic=2) & Q(zone_id=zone_obj.id))
    rr_list_json = serializers.serialize("json", rr_set)
    rr_list = json.loads(rr_list_json)

    # QuerySet 对象无法直接序列化， json.dumps(rr_set) 报下列错误
    # TypeError: Object of type Record is not JSON serializable
    return HttpResponse(json.dumps(rr_list[0]["fields"]))


@login_required
def import_dns(req):
    """
    批量导入DNS记录显示页
    :param req:
    :return:
    """
    if req.method == 'GET':
        zone_id = req.GET.get('zone_id')
        zone_obj = models.Zone.objects.get(id=int(zone_id))
        return render(req, 'bind/import_dns.html', {'zone_obj': zone_obj})
    elif req.method == 'POST':
        file_obj = req.FILES.get('file',)

        fp = xlrd.open_workbook(file_contents=file_obj.read())
        sheet = fp.sheet_by_index(0)
        content_list = []
        for i in range(1, sheet.nrows):
            content_list.append(sheet.row_values(i))
        # print(content_list)
        return render(req,'bind/tmp/import_dns_table_tmp.html',
                      {'content_list': content_list,
                       'DNS_RESOLUTION_LINE': dns_conf.DNS_RESOLUTION_LINE
                       })

def set_style(name, height, bold=False):
    """
    excel样式
    :param name: 字体名
    :param height: 高度
    :param bold: 边框
    :return:
    """
    style = xlwt.XFStyle()  # 初始化样式
    font = xlwt.Font()  # 为样式创建字体
    font.name = name  # 'Times New Roman'
    font.bold = bold
    font.color_index = 000
    font.height = height
    style.font = font

    # 设置单元格边框
    # borders= xlwt.Borders()
    # borders.left= 6
    # borders.right= 6
    # borders.top= 6
    # borders.bottom= 6
    # style.borders = borders

    # 设置单元格背景颜色
    # pattern = xlwt.Pattern()
    # 设置其模式为实型
    # pattern.pattern = pattern.SOLID_PATTERN
    # 设置单元格背景颜色
    # pattern.pattern_fore_colour = 0x00
    # style.pattern = pattern

    return style

@login_required
def export_dns(req):
    """
    导出DNS解析记录
    :param req:
    :return:
    """
    from django.template import loader, Context
    if req.method == 'GET':
        data = req.GET.get('data')
        data = json.loads(data)
        resolution_line = '解析线路 '
        for i in dns_conf.DNS_RESOLUTION_LINE:
                l = '%s:%s ' %(i[0], i[1])
                resolution_line += l
        if data['record_format_type'] == '0':       # 导出excel表格类型数据
            zone_obj = models.Zone.objects.get(id=data['zone_id'])
            record_obj_list = zone_obj.record_set.filter( ~Q(type='SOA') )

            response = HttpResponse(content_type='application/ms-excel')        # 设置response响应头，指定文件类型
            response['Content-Disposition'] = 'attachment; filename="%s.xls"' %(zone_obj.zone_name)   # 设置Content-Disposition 和文件名

            # 生成excel文件 --start
            book = xlwt.Workbook(encoding='utf-8')
            sheet = book.add_sheet(zone_obj.zone_name, cell_overwrite_ok=True)
            row0 = ['主机记录', '记录类型', resolution_line, '记录值', 'MX优先级', 'TTL', '状态', '备注']
            # 设置列宽、高
            sheet.col(0).width = 6000
            sheet.col(1).width = 3000
            sheet.col(2).width = 18000
            sheet.col(3).width = 6000
            sheet.col(4).width = 3000
            sheet.col(5).width = 3000
            sheet.col(6).width = 3000
            sheet.col(7).width = 12000

            for i in range(0, len(row0)):
                sheet.write_merge(0, 0, i, i, row0[i], set_style('Times New Roman', 220, True))

            for k, v in enumerate(record_obj_list, start=1):
                sheet.write(k, 0, v.host)
                sheet.write(k, 1, v.type )
                sheet.write(k, 2, v.resolution_line )
                sheet.write(k, 3, v.data )
                sheet.write(k, 4, v.mx_priority )
                sheet.write(k, 5, v.ttl)
                sheet.write(k, 6, v.status)
                sheet.write(k, 7, v.comment )
            # 生成excel文件 --end

            book.save(response)    # excel文件保存到 http请求 stream中

            return response
        elif data['record_format_type'] == '1':     # 导出zone文本类型数据
            domain_obj = {}
            zone_obj = models.Zone.objects.get(id=data['zone_id'])
            record_obj_soa = zone_obj.record_set.get(type='SOA')
            record_obj_ns = zone_obj.record_set.filter( Q(type='NS') )
            record_obj_other = zone_obj.record_set.filter( ~Q(type__in=['SOA', 'NS']) )

            domain_obj['SOA'] = record_obj_soa
            domain_obj['NS'] = record_obj_ns
            domain_obj['OTHER'] = record_obj_other
            domain_obj['resolution_line_info'] = resolution_line

            response = HttpResponse(content_type='text/plain; charset=utf-8')       # 设置response响应头，指定文件类型
            response['Content-Disposition'] = 'attachment; filename="%s.txt"' %(zone_obj.zone_name)       # 设置Content-Disposition和文件名
            t = loader.get_template('bind/tmp/export_dns_record.txt')
            # c = Context({'domain_obj': domain_obj})
            response.write(t.render({'domain_obj': domain_obj}))  # 通过template模板渲染成文件流
            return response

    if req.method == 'POST':
        msg = {'status': 200}
        return HttpResponse(json.dumps(msg))

# def write_excel(filepath):
#     """
#     生成excel文件并保存到本地
#     :param filepath:
#     :return:
#     """
#     book = xlwt.Workbook(encoding='utf-8')
#     sheet = book.add_sheet('Sheet1', cell_overwrite_ok=True)
#     row = ['主机记录', '记录类型', '解析线路', '记录值', 'MX优先级', 'TTL', '状态', '备注']
#     zone_obj = models.Zone.objects.get(zone_name='paiconf.com')
#     record_obj_list = zone_obj.record_set.filter( ~Q(type='SOA') )
#
#     for i in range(0, len(row)):
#         sheet.write_merge(0, 0, i, i, row[i], set_style('Times New Roman', 220, True))
#     for k, v in enumerate(record_obj_list, start=1):
#         sheet.write(k, 0, v.host)
#         sheet.write(k, 1, v.type )
#         sheet.write(k, 2, v.resolution_line )
#         sheet.write(k, 3, v.data )
#         sheet.write(k, 4, v.mx_priority )
#         sheet.write(k, 5, v.ttl)
#         sheet.write(k, 6, v.status)
#         sheet.write(k, 7, v.comment )
#     book.save(filepath)


@login_required
def dlist_page(req):
    """ 我的域名 页面的 page翻页操作
    :param req: 用户请求
    :return: render模板
    """
    if req.method == 'POST':
        data = json.loads(req.POST.get('data'))
        zone_obj_list = None
        search_key = ''
        if data['action'] == 'pagination':
            zone_obj_list = models.Zone.objects.all().order_by('id')
        elif data['action'] == 'search':
            try:
                search_key = data['other']['search_key']
                zone_obj_list = models.Zone.objects.filter(Q(zone_name__icontains=search_key) | Q(comment__icontains=search_key)).order_by('id')
            except Exception as e:
                print(e)
        zone_obj_perpage_list, pagination_html  = MyPaginator(zone_obj_list, data['page'], data['perpage_num'])

    ret = render(req, 'bind/tmp/domain_table_tmp.html',
                 {'zone_obj_list': zone_obj_perpage_list,
                  'pagination_html': pagination_html,
                  'search_key':search_key
                  })
    ret.set_cookie('perpage_num', data['perpage_num'] or 20)
    return ret

@login_required
def domain_resolution_page(req):
    """
    domain resolution翻页操作
    :param req:
    :return:
    """

    if req.method == 'POST':

        data = json.loads(req.POST.get('data'))
        zone_obj_list = None
        if data['action'] == 'pagination':
            zone_obj_list = models.Zone.objects.all().order_by('id')
        elif data['action'] == 'search':
            try:
                search_key = data['other']['search_key']
                zone_obj_list = models.Zone.objects.filter(Q(zone_name__icontains=search_key) | Q(comment__icontains=search_key)).order_by('id')
            except Exception as e:
                print(e)
        zone_obj_perpage_list, pagination_html  = MyPaginator(zone_obj_list, data['page'], data['perpage_num'])

    else:
        zone_obj_list = models.Zone.objects.all().order_by('id')
        zone_obj_perpage_list, pagination_html  = MyPaginator(zone_obj_list, 1)

    ret = render(req, 'bind/tmp/domain_resolution_table_tmp.html',
                  {'zone_obj_list': zone_obj_perpage_list,
                    'pagination_html':pagination_html,
                   })
    return ret

def  MyPaginator(obj_set, page=1, perpage_num=20, pagiformart=[1, 3, 1]):
    """
    自定义分页器

    :param obj_set: set
        对象集
    :param page: int
        当前查看页页码（活动页）
    :param perpage_num: int
        每页展示对象数量，最大不超过100
    :param pagiformart: list
        分页格式，左、中、右 显示个数
    :return: str
        分页后的子对象集,前端分页导航条html
        注意把 前端分页导航条html(pagination_html) 传到模板
    """

    if not obj_set:     # obj_set 为空
        sub_obj_set = None
        pagination_html = ' '
        return sub_obj_set, pagination_html

    # 上一页 1 2 ... 4 5 6 ... 9 10 下一页         #导航条示例
    L_NUM = pagiformart[0]       # 导航条左边显示个数
    M_NUM = pagiformart[1]//2 * 2 + 1     # 导航条中间显示个数，只能为大于1的奇数,如3、5、7 ...
    R_NUM = pagiformart[2]       # 导航条左边显示个数
    perpage_num = int(perpage_num)
    # perpage_num 最大不超过100，一次性展示太多数据影响性能
    if perpage_num > 100: 
        perpage_num = 100
    paginator = Paginator(obj_set, int(perpage_num))
    if type(page) == str:
        try:
            page = int(page)
        except ValueError:
            page = 1

    if page == 0:       # 查看最后一页
        page = paginator.num_pages
    elif page < 0:      # 查看页码为负数（正常情况不允许查看页码为负数）
        page = 1

    try:
        sub_obj_set = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        sub_obj_set = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        page = paginator.num_pages
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

    input_page = '''
<div class="form-inline">
    <input type="text" size="4" class="form-control" name="input_page_number" id="input_page" placeholder="输入页码">
    <button type="submit" name="jump-page" class="btn btn-primary">跳转</button>
</div>
'''

    per_page = '''
<div class="dropup">
    <button class="btn btn-default dropdown-toggle" value="%s" type="button" id="perpage-dropdownMenu" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
        <span>%s条/页</span>
        <span class="caret"></span>
    </button>
    <ul class="dropdown-menu" aria-labelledby="perpage-dropdownMenu">
        <li value="10"><a href="#">10条/页</a></li>
        <li value="20"><a href="#">20条/页</a></li>
        <li value="50"><a href="#">50条/页</a></li>
        <li value="100"><a href="#">100条/页</a></li>
    </ul>
</div>
''' %(perpage_num, perpage_num)


    pagination_html = \
'''<!-- 分页导航条 -->
<div class="col-md-12">
    <div class="pagination btn pull-left">共%s条</div>
    <div class="pull-left">
        <nav aria-label="pagination-1">
        %s
        %s
        %s
        </nav>
    </div>
    <div class="pagination margin-L10">%s</div>
    <div class="pagination">%s</div>
</div>
<!-- end 分页导航条 -->
''' %(paginator.count, pagination_prev_element, pagination_middle_element, pagination_next_element, input_page, per_page )
    # end 拼接前端的分页导航条html ##

    return sub_obj_set, pagination_html

@login_required
def record_list(req, zone_id):
    """
    域名解析展示列表
    :param req:
    :return:
    """
    is_search = 0
    if req.method == "POST":
        data = json.loads(req.POST.get('data'))
        if 'page' in data.keys():
            page = int(data['page'])
        else:
            page = 1
    else:
        page = 1
    zone_obj = models.Zone.objects.get(id=zone_id)
    record_obj_list = zone_obj.record_set.filter(basic__in=dns_conf.BASIC_SET2SHOW).order_by('id')

    record_obj_perpage_list, pagination_html  = MyPaginator(record_obj_list, page)
    return render(req, 'bind/record_list.html',
                  {'record_obj_list': record_obj_perpage_list,
                   'pagination_html': pagination_html,
                   'zone_obj': zone_obj,
                   'DNS_RESOLUTION_LINE': dns_conf.DNS_RESOLUTION_LINE,
                   'is_search': is_search
                   })

@login_required
def rlist_page(req):
    """
    DNS记录 page翻页操作
    :param req:
    :return: render模板
    """
    if req.method == 'POST':
        data = json.loads(req.POST.get('data'))
        zone_obj = models.Zone.objects.get(id=data['zone_id'])
        record_obj_list = None
        search_key = data['other']['search_key'] or ''

        # 查询出符合条件的 Record
        if data['action'] == 'pagination':
            if search_key == '':
                # basic code 含义 0:可重复非基础记录, 1:可重复基础记录， 2:不可重复基础记录，3:被显性URL或隐性URL关联的记录 ，200:隐性URL转发，301:显性URL 301重定向，302:显性URL 302重定向
                record_obj_list = zone_obj.record_set.filter(basic__in=dns_conf.BASIC_SET2SHOW).order_by('id')
            else:
                record_obj_list = zone_obj.record_set.filter(Q(basic__in=dns_conf.BASIC_SET2SHOW) & (Q(host__icontains=search_key) | Q(data__icontains=search_key) | Q(comment__icontains=search_key) ) ).order_by('id')
        elif data['action'] == 'search':
            try:
                record_obj_list = zone_obj.record_set.filter(Q(basic__in=dns_conf.BASIC_SET2SHOW) & (Q(host__icontains=search_key) | Q(data__icontains=search_key) | Q(comment__icontains=search_key) ) ).order_by('id')

            except Exception as e:
                print(e)
        record_obj_perpage_list, pagination_html  = MyPaginator(record_obj_list, data['page'], data['perpage_num'])

    ret = render(req, 'bind/tmp/domain_record_table_tmp.html',
                  {'record_obj_list': record_obj_perpage_list,
                   'pagination_html': pagination_html,
                   'zone_obj': zone_obj,
                   'DNS_RESOLUTION_LINE': dns_conf.DNS_RESOLUTION_LINE,
                   # 'history_search_key':search_key
                   })
    ret.set_cookie('perpage_num', data['perpage_num'] or 20)
    return ret

def associate_cname_rr_add(rr_data:dict) -> models.Record:
    """新建一条给指定的显性URL 或 隐性URL 关联的 CNAME 记录

    :param rr_data: 用于新建 RR 的raw数据，类型为 dict
    :return: 新建 或 更新的 对象
    """
    # models.Record.objects.update_or_create() 返回结果为
    # Return a tuple (object, created), where created is a boolean
    # cname_rr 的 data 数据从数据库中读取
    rr_cname_raw = {
        'host': rr_data['host'],
        'type': 'CNAME',
        'data': get_url_forwarder_fqdn(),
        'ttl': rr_data['ttl'],
        'basic': 3,
        'zone_id': rr_data['zone_id']
    }
    obj, opt_type = models.Record.objects.update_or_create(**rr_cname_raw)
    return obj

def associate_rr_del(rr:models.Record):
    """ 删除 URL显性、URL隐性 记录关联的 record

    :param rr: 类型为dict
    :return:
    """
    rr_obj = models.Record.objects.get(id=rr.associate_rr_id)
    if rr_obj:
        return rr_obj.delete()

def associate_rr_status_mod(rr:models.Record, status:str):
    """ 修改URL显性、URL隐性 RR 关联的 record 的 status 属性(CNAME RR)

    :param rr: 类型为dict
    :param status: RR 状态。
    :return:
    """
    if not is_forward_rr(rr):
        return
    rr_obj = models.Record.objects.get(id=rr.associate_rr_id)
    if not rr_obj:
        return

    rr_obj.status = status
    rr_obj.update_time = timezone.now()
    rr_obj.save()

def associate_rr_main_mod(rr:models.Record, rr_update_data:dict):
    """ 在一条 RR 更新数据后，处理后续的关联操作。

    :param rr: URL显性 或 URL隐性 RR
    :param rr_update_data: URL显性 或 URL隐性 RR 要更新的数据(dict)
    :return:
    """
    if (not is_forward_rr(rr)) and is_forward_rr_update_data(rr_update_data):
        # 非URL转发RR 更新为 URL转发RR --start
        rr_obj = associate_cname_rr_add(rr_update_data)
        if not rr_obj:
            return
        rr.associate_rr_id = rr_obj.id
        rr.save()
        # 与 rr 关联的 CNAME RR 状态与 rr 的状态保持相同。
        rr_obj.status = rr.status
        rr_obj.save()
        return
        # 非URL转发RR 更新为 URL转发RR --end
    elif is_forward_rr(rr) and is_forward_rr_update_data(rr_update_data):
        # URL显性 或 URL隐性RR更新数据，保持URL转发类型  --start
        associate_rr = models.Record.objects.get(id=rr.associate_rr_id)
        if not associate_rr:
            return
        count = 0
        # 更新 host
        if associate_rr.host != rr_update_data['host']:
            associate_rr.host = rr_update_data['host']
            count += 1
        ## 更新 resolution_line
        if rr.resolution_line != rr_update_data['resolution_line']:
            associate_rr.resolution_line = rr_update_data['resolution_line']
            count += 1

        if count > 0:
            associate_rr.update_time = timezone.now()
            associate_rr.save()
        # URL显性 或 URL隐性RR更新数据，保持URL转发类型 --end

    elif is_forward_rr(rr) and (not is_forward_rr_update_data(rr_update_data)):
        # URL显性 或 URL隐性RR更新数据，更新为非URL转发类型  --start
        associate_rr = models.Record.objects.get(id=rr.associate_rr_id)
        if not associate_rr:
            return
        rr.associate_rr_id = None
        rr.basic = 0
        rr.save()
        associate_rr.delete()
        # URL显性 或 URL隐性RR更新数据，更新为非URL转发类型  --end


@login_required
def record_add(req):
    """
    添加解析记录，批量导入DNS记录
    接收到的data： [{"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "comment":_comment, "zone":_zone_name }]
    :param req:
    :return:
    """
    if req.method == 'POST':
        data = req.POST.get('data')
        msg = {'status': 500, 'total':0, 'success_total':0}
        try:
            data = json.loads(data)
            msg['total'] = len(data)
            for rr_raw in data:
                if not a_record_data_filter(rr_raw):
                    print("%s 检查过滤RR数据失败。" % rr_raw)
                    continue
                # 新建 显性URL、隐性URL 记录时，需要创建一条关联的 CNAME 记录  --start
                if type(rr_raw) == dict and 'basic' in list(rr_raw.keys()):
                    if rr_raw['type'] == 'TXT' and rr_raw['basic'] in (dns_conf.URL_FORWARDER_BASIC_SET):
                        obj = associate_cname_rr_add(rr_raw)
                        rr_raw['associate_rr_id'] = obj.id
                # 新建 显性URL、隐性URL 记录时，需要创建一条关联的 CNAME 记录  --end
                # TXT 类型的 RR 的值超过 255 个字符时需要分割成多个字符串
                if rr_raw['type'] == 'TXT':
                    rr_raw['data'] = split_txt(rr_raw['data'])
                # 创建 RR
                models.Record.objects.update_or_create(**rr_raw)
                msg['success_total'] += 1
            if msg['success_total'] == 0:
                msg['status'] = 500
            else:
                msg['status'] = 200
        except Exception as e:
            print(e)
        return HttpResponse(json.dumps(msg))
    else:
        return HttpResponse(COMMON_MSG['req_use_post'])

@login_required
def record_del(req):
    """

    :param req:
    :return:
    """
    if req.method == 'POST':
        msg = {'status': 500}
        # 要删除的 rr id 的 list
        data = json.loads(req.POST.get('data'))
        # print(data)
        success_count = 0
        total_count = len(data)
        for i in data:
            try:
                record_obj = models.Record.objects.get(id=i)
                # 删除 显性URL、隐性URL 记录时，同时删除与其关联的 CNAME 记录 --start
                if record_obj.type == 'TXT' and record_obj.basic in dns_conf.URL_FORWARDER_BASIC_SET:
                    associate_rr_del(record_obj)
                # 删除 显性URL、隐性URL 记录时，同时删除与其关联的 CNAME 记录 --end
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

@login_required
def record_mod(req):
    """
    修改DNS记录
    :param req:
    :return:
    """
    msg = {'status': 500}
    _type = req.GET.get('type')      #  <==>  type = req.GET['type'] ,两种用法都可以
    if req.method == 'POST':
        data:dict = json.loads(req.POST.get('data'))  # 一条 json 格式的更新RR 操作数据(dict类型)
        if type(data) != dict:
            return HttpResponse(COMMON_MSG['req_use_post'])
        if _type == 'status':        # 修改status，开启、停用DNS记录
            if not data['id_list']:
                return HttpResponse(COMMON_MSG['req_use_post'])
            record_obj_set = models.Record.objects.filter(id__in=data['id_list'])
            if not record_obj_set:
                return HttpResponse(COMMON_MSG['req_use_post'])
            try:
                record_obj_set.update(status=action2status(data['action']))

                # 更新 update_time
                record_obj_set.update(update_time=timezone.now())
                # 更新相关联的记录
                for rr in record_obj_set:
                    associate_rr_status_mod(rr, action2status(data['action']))

                msg['status'] = 200
            except Exception as e:
                print(e)

        elif _type == 'main':      # 修改DNS记录除status外的项
            try:
                record_set = models.Record.objects.filter(id=data['id'])
                del(data['id'])     # data.pop('id') 则会 print key
                zone_obj = record_set.first().zone
                data['update_time'] = timezone.now()
                a_record_data_filter(data)

                # 更新相关联的记录，要在“更新 record_obj_set” 之前执行，否则 record_obj_set 会更新
                for rr in record_set:
                    associate_rr_main_mod(rr, data)
                # 更新 record_obj_set
                if 'zone_id' in data.keys():  # 因为 data['zone'] = zone_obj 也包含了字段 ‘zone_id’
                    del(data['zone_id'])
                data['zone'] = zone_obj
                # TXT 类型的 RR 的值超过 255 个字符需要分割成多个字符串
                if data['type'] == 'TXT':
                    data['data'] = split_txt(data['data'])
                # 更新 RR
                record_set.update(**data)

                msg['status'] = 200
            except Exception as e:
                print(e)

        return HttpResponse(json.dumps(msg))
    else:
        return HttpResponse(COMMON_MSG['req_use_post'])

def is_forward_rr(rr:models.Record) -> bool:
    """ 判断一个 RR 记录是否为 URL转发 记录

    :param rr:
    :return:
    """
    if not rr.associate_rr_id:
        return False
    return (rr.type == 'TXT') and (rr.basic in dns_conf.URL_FORWARDER_BASIC_SET)

def is_forward_rr_update_data(rr_update_data:dict) -> bool:
    """ 判断一个 RR更新数据 是否为 URL转发 类型

    :param rr_update_data: RR更新数据
    :return:
    """
    if (type(rr_update_data) == dict) and ('basic' in list(rr_update_data.keys())):
        if (rr_update_data['type'] == 'TXT') and (rr_update_data['basic'] in dns_conf.URL_FORWARDER_BASIC_SET):
            return True

    return False
