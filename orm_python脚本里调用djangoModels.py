#!/use/bin/env python
# -*- coding:utf-8 -*-

import os, django

# os.environ['DJANGO_SETTINGS_MODULE'] = 'prj_d18.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bindUI.settings")
# import django
django.setup()

# 必须在django.setup()  后才能导入
from DnsRecord import models

from django.db.models import F
from django.db.models import Q
from django.db.models import Avg, Max, Sum, Count, Min


zone_tag_obj = models.ZoneTag.objects.get(id=1)
record_obj_list = zone_tag_obj.ZoneTag_Record.all()

print(zone_tag_obj)
print(record_obj_list)
for i in record_obj_list:
    print(i.host, i.type, i.data, i.comment, i.mx_priority)

