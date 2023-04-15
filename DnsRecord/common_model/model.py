"""
基础 Model
"""

from django.db import models

class BasicModel(models.Model):
    create_time = models.DateTimeField('create_time', auto_now_add=True, null=True)
    update_time = models.DateTimeField('update_time', auto_now=True, null=True)
    comment = models.CharField('comment', max_length=255, null=True, blank=True, default=None, help_text='备注')

    class Meta:
        # 设置为抽象类
        abstract = True
