from django.db import models
from .common_model.model import BasicModel
import sys, os
BASIC_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(BASIC_DIR)
from bindUI import dns_conf



# Create your models here.

record_type_choices = (
    ('A','A'),
    ('CNAME','CNAME'),
    ('MX','MX'),
    ('TXT','TXT'),
    ('NS','NS'),
    ('AAAA','AAAA'),
    ('SRV','SRV'),
    ('PTR','PTR'),
    ('SOA','SOA'),
    ('CAA','CAA'),
    ('URI','URI'),
    # ('EXPLICIT_URL','EXPLICIT_URL'),  # 显性URL
    # ('IMPLICIT_URL','IMPLICIT_URL'),  # 隐性URL
)

status_choices = (
    ('on', '开启'),
    ('off', '暂停'),
)

class Record(BasicModel):
    """
    DNS records

    """
    zone = models.CharField('zone', max_length=255)
    host = models.CharField('host', max_length=255, default='@', db_index=True, help_text='Host name or IP address')
    type = models.CharField('type', max_length=64, choices=record_type_choices, default= 'A', help_text='DNS data type')
    data = models.CharField('data', max_length=255, help_text='IP address / Host name / Full domain name')
    ttl = models.IntegerField('ttl', null=True, blank=True, default=None, help_text='Time to live')
    mx_priority = models.CharField('mx_priority', max_length=255, null=True, blank=True, default=None, help_text='MX Priority')
    refresh = models.IntegerField('refresh', null=True, blank=True, default=None, help_text='Refresh time for SOA record,Slave DNS向Master DNS进行Serial对比同步间隔时间,Master DNSnotify参数关闭时有效')
    retry = models.IntegerField('retry', null=True, blank=True, default=None, help_text='Retry time for SOA record,当Slave DNS获取Master DNS Serial更新失败时,重试时间')
    expire = models.IntegerField('expire', null=True, blank=True, default=None, help_text='Expire time for SOA record,Slave DNS在没有Master DNS的情况下权威地提供域名解析服务的时间')
    minimum = models.IntegerField('minimum', null=True, blank=True, default=None, help_text='Minimum time for SOA record(default TTL),最小默认 TTL 值，在未定义全局$TTL时，就会以此值为准')
    serial = models.BigIntegerField('serial', null=True, blank=True, default=None, help_text='serial for SOA record,Zone序列号,不超过10位数字')
    mail = models.CharField('mail', max_length=255, null=True, blank=True, default=None, help_text='Responsible person mail for SOA record')
    primary_ns =  models.CharField('primary_ns', max_length=255, null=True, blank=True, default=None, help_text='Primary name server for SOA record,slav DNS指定Master DNS')
    status = models.CharField('status', max_length=3, choices=status_choices, default='on',help_text='record on/off status')
    resolution_line = models.CharField('resolution_line', max_length=32,choices=dns_conf.DNS_RESOLUTION_LINE, default='0', help_text='解析线路')
    zone_tag = models.ForeignKey('ZoneTag', related_name='ZoneTag_Record', on_delete=models.PROTECT)
    basic = models.IntegerField('basic', default=0, help_text='是否为基础记录，记录是否允许重复。0:可重复非基础记录, 1:可重复基础记录， 2:不可重复基础记录，3:被显性URL或隐性URL关联的记录 ，200:隐性URL转发，301:显性URL 301重定向，302:显性URL 302重定向')
    associate_rr_id = models.IntegerField('associate_rr_id', null=True, blank=True, default=None, help_text='关联的 Resource Record ID，用于显性URL、隐性URL')
    # create_time = models.DateTimeField('create_time', auto_now_add=True)
    # update_time = models.DateTimeField('update_time', auto_now=True)
    # comment = models.CharField('comment', max_length=255, null=True, blank=True, default=None, help_text='备注')

    def __str__(self):
        return(self.host)

    class Meta:
        # app_label 指定 app 标识，缺省为 app name
        # app_label = ''
        # 定义表名。默认为 app_label + "_" + model_name的小写
        db_table = 'record'
        # Admin 后台显示的表名
        verbose_name = verbose_name_plural = "Record"

class ZoneTag(BasicModel):
    """
    zone tag
    """
    zone_name = models.CharField('zone name', max_length=255, unique=True, db_index=True)
    status = models.CharField('status', max_length=3, choices=status_choices, default='on',help_text='zone on/off status')
    # create_time = models.DateTimeField('create_time', auto_now_add=True, null=True)
    # update_time = models.DateTimeField('update_time', auto_now=True, null=True)
    # comment = models.CharField('注释', max_length=255, null=True, blank=True)

    def __str__(self):
        return self.zone_name

    class Meta:
        # 定义表名
        db_table = 'zonetag'
        # Admin 后台显示的表名
        verbose_name = verbose_name_plural = "ZoneTag"

