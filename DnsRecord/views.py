from django.shortcuts import render, redirect
from . import models

# Create your views here.

def root(req):
    return redirect('/')

def index(req):
    """
    首页
    :param req:
    :return:
    """
    return render(req, 'bind/index.html')
