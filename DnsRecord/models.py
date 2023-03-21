from django.db import models
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
    ('EXPLICIT_URL','EXPLICIT_URL'),
    ('IMPLICIT_URL','IMPLICIT_URL'),
)

status_choices = (
    ('on', '开启'),
    ('off', '暂停'),
)

class Record(models.Model):
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
    serial = models.BigIntegerField('serial', null=True, blank=True, default=None, help_text='serial # for SOA record,Zone序列号,不超过10位数字')
    resp_person = models.CharField('resp_person', max_length=255, null=True, blank=True, default=None, help_text='Responsible person mail for SOA record')
    primary_ns =  models.CharField('primary_ns', max_length=255, null=True, blank=True, default=None, help_text='Primary name server for SOA record,slav DNS指定Master DNS')
    status = models.CharField('status', max_length=3, choices=status_choices, default='on',help_text='record on/off status')
    create_time = models.DateTimeField('create_time', auto_now_add=True)
    update_time = models.DateTimeField('update_time', auto_now=True)
    comment = models.CharField('comment', max_length=255, null=True, blank=True, default=None, help_text='备注')
    resolution_line = models.CharField('resolution_line', max_length=32,choices=dns_conf.DNS_RESOLUTION_LINE, default='0', help_text='解析线路')
    zone_tag = models.ForeignKey('ZoneTag', related_name='ZoneTag_Record', on_delete=models.PROTECT)
    basic = models.IntegerField('basic', default=0, help_text='是否为基础记录，记录是否允许重复。0:可重复非基础记录, 1:可重复基础记录， 2:不可重复基础记录，200:隐性URL转发，301:显性URL 301重定向，302:显性URL 302重定向')

    def __str__(self):
        return(self.host)

class ZoneTag(models.Model):
    """
    zone tag
    """
    zone_name = models.CharField('zone name', max_length=255, unique=True, db_index=True)
    comment = models.CharField('注释', max_length=255, null=True, blank=True)
    status = models.CharField('status', max_length=3, choices=status_choices, default='on',help_text='record on/off status')

    def __str__(self):
        return self.zone_name


