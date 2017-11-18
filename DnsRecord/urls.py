"""bindUI URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^domains/list', views.domain_list, name='domain_list'),
    url(r'^domains/rlist', views.domain_resolution_list, name='domain_resolution_list'),
    url(r'^dns/(?P<domain_id>\d+)', views.record_list, name='record_list'),
    url(r'^dns/add.html', views.record_add, name='record_add'),
    url(r'^dns/del.html', views.record_del, name='record_del'),
    url(r'^dns/mod.html', views.record_mod, name='record_mod'),
    url(r'^dns/rr_api/list.json', views.record_mod, name='record_mod'),
    url(r'^dns/rlist_page.html', views.rlist_page, name='/rlist_page'),
    url(r'^$', views.index),
]

