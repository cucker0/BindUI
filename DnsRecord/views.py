from django.shortcuts import render, redirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from . import models
from django.db.models import Q
from django.utils import timezone
import xlrd, xlwt

import sys, os
BASIC_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASIC_DIR)
from bindUI import dns_conf
import json
from .utils import serial, record_data_filter, COMMON_MSG

# Create your views here.

"""
msg = {'status': code}
code 值含义
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
    return render(req, 'bind/index.html')

@login_required
def domain_list(req):
    """
    dashboard, domain list
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
    zone_obj_list = models.ZoneTag.objects.all()
    zone_obj_perpage_list, pagination_html = MyPaginator(zone_obj_list, page)
    return render(req, 'bind/domain_list.html', {
        'zone_obj_list': zone_obj_list,
        'pagination_html':pagination_html,
    })

@login_required
def domain_status_mod(req):
    """
    修改doamin状态值，即开启或停用
    :param req:
    :return:
    """
    msg = {'status': 500}
    if req.method == 'POST':
        data = json.loads(req.POST.get('data'))
        if data['id_list']:
            print(data['id_list'], type(data['id_list']))
            zone_tag_list = models.ZoneTag.objects.filter(id__in=data['id_list'])
        try:
            if data['action'] == '_turnOff':
                zone_tag_list.update(status='off')
            else:
                zone_tag_list.update(status='on')
            msg['status'] = 200
        except Exception as e:
            print(e)
    return msg

@login_required
def domain_curd(req):
    """
    域名增改查删
    :param req:
    :return:
    """
    resp = ''
    _type = req.GET.get('type').strip()
    if _type == 'c':        # 新增domain
        resp = domain_add(req)
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
            zone_tag_list = models.ZoneTag.objects.filter(id__in=data['id_list'])
            try:
                for zone_tag_obj in zone_tag_list:
                    record_set = zone_tag_obj.ZoneTag_Record.all()
                    record_set.delete()     # 删除dns记录
                zone_tag_list.delete()      # 删除zone_tag
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
        data = json.loads(req.GET.get('data'))
    except Exception as e:
        print(e)

    data['type'] = 'SOA'
    data['basic'] = 2       # 标识为不可重复基础记录
    data['host'] = '@'
    data['ttl'] = 3600
    data['serial'] = serial()
    data = record_data_filter(data)
    record_set = models.Record.objects.filter(Q(type='SOA') & Q(zone=data['zone'].strip()) )
    zone_tag_set = models.ZoneTag.objects.filter(zone_name=data['zone'].strip())

    if zone_tag_set:
        msg['msg'] += "zone_tag:%s exist; " %(data['zone'])
    else:
        zone_tag_ins = { 'zone_name':data['zone'] }
        try:
            if data['comment']:
                zone_tag_ins['comment'] = data['comment']
        except KeyError:
            zone_tag_ins['comment'] = None

        models.ZoneTag.objects.create(**zone_tag_ins)

    if record_set:
        msg['msg'] += "record SOA:%s exist!; " %(data['zone'])
    else:
        try:
            zone_tag_obj = models.ZoneTag.objects.get(zone_name=data['zone'].strip())
            data['zone_tag'] = zone_tag_obj
            models.Record.objects.create(**data)
            msg['status'] = 200
            msg['msg'] = "%s create success." %(data['zone'])
        except Exception as e:
            print(e)
    return msg


def domain_ns(req):
    """
    domain NS记录创建、修改
    :param req:
    :return:
    """
    msg = {'status': 500, 'msg':''}
    try:
        data = json.loads(req.GET.get('data'))
        zone = data['zone'].strip()
        ns_submit_set = set(data['ns_list'])        # 提交更新的domain NS集合
        zone_tag_obj = models.ZoneTag.objects.get(zone_name=zone)
        if zone_tag_obj:        # zone必须存在
            ns_obj_set = models.Record.objects.filter(Q(host='@') & Q(type='NS') & Q(zone=zone))
            ns_data_set = set()
            for i in ns_obj_set:
                ns_data_set.add(i.data)        # 数据库中已经存在domain NS集合
            ns_toadd_set = ns_submit_set - ns_data_set      # 需要创建的domain NS data字段集合
            ns_todelete_set = ns_data_set - ns_submit_set   # 需要删除的domian NS data字段集合
            for i in ns_toadd_set:
                ns_instance = {'zone':zone, 'host':'@', 'type':'NS', 'data':i.strip(), 'ttl':10800, 'basic':2, 'zone_tag':zone_tag_obj }
                record_data_filter(ns_instance)
                models.Record.objects.update_or_create(**ns_instance)
                msg['msg'] += "domain ns:%s create success; " %(i.strip())

            ns_todele_obj_set = models.Record.objects.filter(data__in=ns_todelete_set)
            ns_todele_obj_set.delete()
            for i in ns_toadd_set:
                msg['msg'] += "domain ns:%s delete success; " %(i.strip())

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
    zone_obj_list = models.ZoneTag.objects.all()
    zone_obj_perpage_list, pagination_html  = MyPaginator(zone_obj_list, 1, 10)
    return render(req, 'bind/domain_resolution_list.html',
                  {'zone_obj_list': zone_obj_perpage_list,
                    'pagination_html':pagination_html,
                   })

@login_required
def domain_man(req, domain_id, optype):
    """
    域名管理
    :param req:
    :return:
    """
    domain_id = int(domain_id)
    zone_tag_obj = models.ZoneTag.objects.get(id=domain_id)
    ns_set = models.Record.objects.filter(Q(type='NS') & Q(basic=2) & Q(zone_tag=zone_tag_obj))
    return render(req, 'bind/domain_manager.html', {'zone_tag_obj':zone_tag_obj, 'ns_set': ns_set})

@login_required
def import_dns(req):
    """
    批量导入DNS记录显示页
    :param req:
    :return:
    """
    if req.method == 'GET':
        domain = req.GET.get('domain')
        return render(req, 'bind/import_dns.html', {'domain':domain })
    elif req.method == 'POST':
        data = {'status':0}
        file_obj = req.FILES.get('file',)

        fp = xlrd.open_workbook(file_contents=file_obj.read())
        sheet = fp.sheet_by_index(0)
        content_list = []
        for i in range(1, sheet.nrows):
            content_list.append(sheet.row_values(i))
        # print(content_list)
        return render(req, 'bind/tmp/import_dns_table_tmp.html', {'content_list': content_list, 'DNS_RESOLUTION_LINE':dns_conf.DNS_RESOLUTION_LINE})

def set_style(name, height, bold=False):
    """
    excel样式
    :param name: 字体名
    :param height: 调度
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
        if data['export_dns_record_type'] == '0':       # 导出excel表格类型数据
            zone_tag_obj = models.ZoneTag.objects.get(zone_name=data['zone'])
            record_obj_list = zone_tag_obj.ZoneTag_Record.filter( ~Q(type='SOA') )

            response = HttpResponse(content_type='application/ms-excel')        # 设置response响应头，指定文件类型
            response['Content-Disposition'] = 'attachment; filename="%s.xls"' %(data['zone'])   # 设置Content-Disposition 和文件名

            # 生成excel文件
            book = xlwt.Workbook(encoding='utf-8')
            sheet = book.add_sheet('Sheet1', cell_overwrite_ok=True)
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
            # 生成excel文件完成

            book.save(response)    # excel文件保存到 http请求 stream中

            return response
        elif data['export_dns_record_type'] == '1':     # 导出zone文本类型数据
            domain_obj = {}
            zone_tag_obj = models.ZoneTag.objects.get(zone_name=data['zone'])
            record_obj_soa = zone_tag_obj.ZoneTag_Record.get(type='SOA')
            record_obj_ns = zone_tag_obj.ZoneTag_Record.filter( Q(type='NS') )
            record_obj_other = zone_tag_obj.ZoneTag_Record.filter( ~Q(type__in=['SOA', 'NS', 'PTR']) )

            domain_obj['SOA'] = record_obj_soa
            domain_obj['NS'] = record_obj_ns
            domain_obj['OTHER'] = record_obj_other
            domain_obj['resolution_line_info'] = resolution_line

            response = HttpResponse(content_type='text/plain; charset=utf-8')       # 设置response响应头，指定文件类型
            response['Content-Disposition'] = 'attachment; filename="%s.txt"' %(data['zone'])       # 设置Content-Disposition 和文件名
            t = loader.get_template('bind/tmp/export_dns_record.txt')       # 通过template模板渲染成文件流
            c = Context({
                'configs': domain_obj,
              })
            response.write(t.render(c))
            return response


    elif req.method == 'POST':
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
#     zone_tag_obj = models.ZoneTag.objects.get(zone_name='paiconf.com')
#     record_obj_list = zone_tag_obj.ZoneTag_Record.filter( ~Q(type='SOA') )
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
    """
    我的域名 page翻页
    :param req: 用户请求
    :return: render模板
    """
    if req.method == 'POST':
        data = json.loads(req.POST.get('data'))
        zone_obj_list = None
        search_key = ''
        if data['action'] == 'pagination':
            zone_obj_list = models.ZoneTag.objects.all()
        elif data['action'] == 'search':
            try:
                search_key = data['other']['search_key']
                zone_obj_list = models.ZoneTag.objects.filter(Q(zone_name__icontains=search_key) | Q(comment__icontains=search_key))
            except Exception as e:
                print(e)
        zone_obj_perpage_list, pagination_html  = MyPaginator(zone_obj_list, data['page'], data['perpage_num'])

    ret = render(req, 'bind/tmp/domain_table_tmp.html',
                 {'zone_obj_list': zone_obj_perpage_list,
                  'pagination_html': pagination_html,
                  'search_key':search_key
                  })
    ret.set_cookie('perpage_num', data['perpage_num'] or 10)
    return ret

@login_required
def domain_resolution_page(req):
    """
    domain resolution翻页
    :param req:
    :return:
    """

    if req.method == 'POST':

        data = json.loads(req.POST.get('data'))
        zone_obj_list = None
        if data['action'] == 'pagination':
            zone_obj_list = models.ZoneTag.objects.all()
        elif data['action'] == 'search':
            try:
                search_key = data['other']['search_key']
                zone_obj_list = models.ZoneTag.objects.filter(Q(zone_name__icontains=search_key) | Q(comment__icontains=search_key))
            except Exception as e:
                print(e)
        zone_obj_perpage_list, pagination_html  = MyPaginator(zone_obj_list, data['page'], data['perpage_num'])

    else:
        zone_obj_list = models.ZoneTag.objects.all()
        zone_obj_perpage_list, pagination_html  = MyPaginator(zone_obj_list, 1)

    ret = render(req, 'bind/tmp/domain_resolution_table_tmp.html',
                  {'zone_obj_list': zone_obj_perpage_list,
                    'pagination_html':pagination_html,
                   })
    return ret

def  MyPaginator(obj_set, page=1, perpage_num=10, pagiformart=[1, 3, 1]):
    """
    自定义分页器

    :param obj_set: 对象集
    :param page: 当前查看页页码（活动页）int
    :param perpage_num: 每页展示对象数量,int型
    :param pagiformart: 分页格式，左、中、右 显示个数， list
    :return: 分页后的子对象集,前端分页导航条html
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
    <input type="text" size="4" class="form-control" id="input_page" placeholder="输入页码">
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
def record_list(req, domain_id):
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
    zone_tag_obj = models.ZoneTag.objects.get(id=domain_id)
    record_obj_list = zone_tag_obj.ZoneTag_Record.filter(basic=0)

    record_obj_perpage_list, pagination_html  = MyPaginator(record_obj_list, page)
    return render(req, 'bind/record_list.html',
                  {'record_obj_list': record_obj_perpage_list,
                   'pagination_html': pagination_html,
                   'zone_tag_obj': zone_tag_obj,
                   'DNS_RESOLUTION_LINE': dns_conf.DNS_RESOLUTION_LINE,
                   'is_search': is_search
                   })

@login_required
def rlist_page(req):
    """
    DNS记录 page翻页
    :param req:
    :return: render模板
    """
    if req.method == 'POST':
        data = json.loads(req.POST.get('data'))
        zone_tag_obj = models.ZoneTag.objects.get(zone_name=data['zone'])
        record_obj_list = None
        search_key = data['other']['search_key'] or ''

        if data['action'] == 'pagination':
            if search_key == '':
                record_obj_list = zone_tag_obj.ZoneTag_Record.filter(basic=0)
            else:
                record_obj_list = zone_tag_obj.ZoneTag_Record.filter(Q(basic=0) & (Q(host__icontains=search_key) | Q(data__icontains=search_key) | Q(comment__icontains=search_key) ) )
        elif data['action'] == 'search':
            try:
                record_obj_list = zone_tag_obj.ZoneTag_Record.filter(Q(basic=0) & (Q(host__icontains=search_key) | Q(data__icontains=search_key) | Q(comment__icontains=search_key) ) )

            except Exception as e:
                print(e)
        record_obj_perpage_list, pagination_html  = MyPaginator(record_obj_list, data['page'], data['perpage_num'])

    ret = render(req, 'bind/tmp/domain_record_table_tmp.html',
                  {'record_obj_list': record_obj_perpage_list,
                   'pagination_html': pagination_html,
                   'zone_tag_obj': zone_tag_obj,
                   'DNS_RESOLUTION_LINE': dns_conf.DNS_RESOLUTION_LINE,
                   # 'history_search_key':search_key
                   })
    ret.set_cookie('perpage_num', data['perpage_num'] or 10)
    return ret

@login_required
def record_add(req):
    """
    添加解析记录，批量导入DNS记录
    接收到的data： [{"type":_type, "host":_host, "resolution_line":_resolution_line, "data":_data, "mx_priority":_mx, "ttl":_ttl, "comment":_comment, "zone":_zone_tag_name }]
    :param req:
    :return:
    """
    if req.method == 'POST':
        data = req.POST.get('data')
        msg = {'status': 500, 'total':0, 'success_total':0}
        try:
            data = json.loads(data)
            msg['total'] = len(data)
            for i in data:
                record_data_filter(i)        # 字典或列表 以指针形式传递参数
                zone_tag_obj = models.ZoneTag.objects.get(zone_name=i['zone'].strip())
                i['zone_tag'] = zone_tag_obj
                models.Record.objects.update_or_create(**i)
                msg['success_total'] += 1

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
        data = json.loads(req.POST.get('data'))
        # print(data)
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
        data = json.loads(req.POST.get('data'))
        if _type == 'status':        # 修改staus
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

        elif _type == 'main':      # 修改DNS记录除staus外的项
            try:
                record_obj_set = models.Record.objects.filter(id=data['id'])
                del(data['id'])     # data.pop('id') print key
                # zone_tag_obj = models.ZoneTag.objects.get(zone_name=data['zone'])
                zone_tag_obj = record_obj_set.first().zone_tag
                data['zone'] = zone_tag_obj.zone_name
                data['zone_tag'] = zone_tag_obj
                data['update_time'] = timezone.now()
                record_data_filter(data)
                record_obj_set.update(**data)

                msg['status'] = 200
            except Exception as e:
                print(e)

        return HttpResponse(json.dumps(msg))
    else:
        return HttpResponse(COMMON_MSG['req_use_post'])

