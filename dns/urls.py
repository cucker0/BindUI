"""
URL configuration for BindUI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, re_path
from . import views

urlpatterns = [
    re_path(r'^domains/dlist_page.html', views.dlist_page, name='dlist_page'),
    re_path(r'^domains/list', views.domain_list, name='domain_list'),
    re_path(r'^domains/drlist_page.html', views.domain_resolution_page, name='domain_resolution_page'),
    re_path(r'^domains/rlist', views.domain_resolution_list, name='domain_resolution_list'),
    re_path(r'^domains/domain_curd.html', views.domain_curd, name='domain_curd'),
    re_path(r'^domains/_import_dns.html', views.import_dns, name='import_dns'),
    re_path(r'^domains/_export_dns.html', views.export_dns, name='export_dns'),
    re_path(r'^domains/(?P<zone_id>\d+)/(?P<optype>\w+)', views.domain_man, name='domain_man'),
    re_path(r'^domains/api/get_domain/(?P<zone_id>\d+)', views.get_domain_by_id, name='get_domain_by_id'),


    re_path(r'^dns/(?P<zone_id>\d+)', views.record_list, name='record_list'),
    re_path(r'^dns/add.html', views.record_add, name='record_add'),
    re_path(r'^dns/del.html', views.record_del, name='record_del'),
    re_path(r'^dns/mod.html', views.record_mod, name='record_mod'),
    # re_path(r'^dns/rr_api/list.json', views.record_mod, name='record_mod'),
    re_path(r'^dns/rlist_page.html', views.rlist_page, name='/rlist_page'),
    re_path(r'^$', views.index),
]

