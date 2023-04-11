"""MiliOPS URL Configuration

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
# from django.conf.urls import url, include
from django.urls import include, re_path
from . import views

urlpatterns = [
    re_path(r'login/$', views.MyLogin, name='mylogin'),
    re_path(r'logout/$', views.MyLogout, name='mylogout'),
    re_path(r'userprofile/$', views.UserProfile, name='userprofile'),
    re_path(r'userprofile/(\d{1,2})/$', views.UserProfileRepeater),
    re_path(r'^$', views.MyLogin),
]
