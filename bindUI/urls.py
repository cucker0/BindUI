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
from django.contrib import admin
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^auth/', include("authentication.urls")),
    re_path(r'^', include('dns.urls')),
    # 解决 http://xx/favicon.ico  报404的问题
    # /favicon.ico 302 重定向到 static/favicon.ico
    re_path(r'^favicon.ico$',RedirectView.as_view(url=r'static/favicon.ico')),
]
