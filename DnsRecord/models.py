from django.db import models

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
)

record_status_choices = (
    ('on', '开启'),
    ('off', '暂停'),
)

class Record(models.Model):
    """
    DNS records

    """
    zone = models.CharField('zone', max_length=255)
    host = models.CharField('host', max_length=255, null=True, blank=True,default=None, help_text='Host name or IP address')
    type = models.CharField('type', max_length=64, choices=record_type_choices, null=True, blank=True,default=None, help_text='DNS data type')
    data = models.CharField('data', max_length=255, help_text='IP address / Host name / Full domain name')
    ttl = models.IntegerField('ttl', null=True, blank=True,default=None, help_text='Time to live')
    mx_priority = models.CharField('mx_priority', max_length=255, null=True, blank=True,default=None, help_text='MX Priority')
    refresh = models.IntegerField('refresh', null=True, blank=True,default=None, help_text='Refresh time for SOA record')
    retry = models.IntegerField('retry', null=True, blank=True,default=None, help_text='Retry time for SOA record')
    expire = models.IntegerField('expire', null=True, blank=True,default=None, help_text='Expire time for SOA record')
    minimum = models.IntegerField('minimum', null=True, blank=True,default=None, help_text='Minimum time for SOA record(default TTL)')
    serial = models.BigIntegerField('serial', null=True, blank=True,default=None, help_text='serial # for SOA record')
    resp_person = models.CharField('resp_person', max_length=255, null=True, blank=True,default=None, help_text='Responsible person mail for SOA record')
    primary_ns =  models.CharField('primary_ns', max_length=255, null=True, blank=True,default=None, help_text='Primary name server for SOA record')
    status = models.CharField('status', max_length=3, choices=record_status_choices, default='on')
    create_time = models.DateTimeField('create_time', auto_now_add=True)
    update_time = models.DateTimeField('update_time', auto_now=True)
    comment = models.CharField('comment', max_length=255, null=True, blank=True, default=None, help_text='备注')
    zone_tag = models.ForeignKey('ZoneTag')

    def __str__(self):
        return(self.host)

class ZoneTag(models.Model):
    """
    zone tag
    """
    zone_name = models.CharField('zone name', max_length=255)
    comment = models.CharField('注释', max_length=255, null=True, blank=True)

    def __str__(self):
        return self.zone_name


