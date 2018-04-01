from django.db import models
from django.contrib.auth.models import User     # 导入 user类

# Create your models here.
class UserProfile(models.Model):
    """
    用户表
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField('昵称', max_length=32, default='bind')
    head_portrait_width = models.PositiveIntegerField(default=90)
    head_portrait_height = models.PositiveIntegerField(default=90)
    # 自动获取图片的宽、高值,并自动填充字段 head_portrait_width、head_portrait_height
    # models.ImageField 的upload_to可使用多级目录,如upload/UserProfile/head_img
    head_portrait = models.ImageField(u'头像',width_field='head_portrait_width',height_field='head_portrait_height',null=True,blank=True,upload_to='upload/user_image')
    login_status = models.IntegerField(u'用户登录状态',default=0)

    def __str__(self):
        return self.user.username