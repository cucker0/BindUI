from django.shortcuts import render, HttpResponse, redirect
from . import models
import json, re, time, random
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def MyLogin(req):
    """
    登录
    :param req:
    :return:
    """
    if req.method == "POST":
        data_send = {'auth_status': 0}
        data = req.POST.get('data')
        data = json.loads(data)
        user_auth = authenticate(username=data['user'],
                            password=data['password'])
        if user_auth is not None and user_auth.is_active:        # 认证成功
            data_send['auth_status'] = 1
            userprofile_set = models.UserProfile.objects.filter(user=models.User.objects.filter(username=req.POST.get('username')).first())
            userprofile_set.update(login_status=1)
            login(req, user_auth)
            next_url = req.GET.get('next') or '/'
            # return redirect(next_url)
            data_send['url'] = next_url
            return HttpResponse(json.dumps({'data':data_send}))
        return HttpResponse(json.dumps({'data':data_send}))
    return render(req, 'authentication/login.html/')


def MyLogout(req):
    """
    退出登录
    :param req:
    :return:
    """
    user_set = models.UserProfile.objects.filter(user_id=req.user.id)
    user_set.update(login_status=0)
    logout(req)
    next_url = req.GET.get('next') or '/auth/login/'
    return redirect(next_url)

@login_required
def UserProfile(req):
    return render(req, 'authentication/userprofile.html')

def UserProfileRepeater(req,action_code=0):
    """
    用户设置 操作类型分发器
    :param req:
    :param action_code:
    :return:
    """
    if action_code == '1':
        return ChangePassword(req)
    elif action_code == '2':
        return UploadFile(req)
    elif action_code == '3':
        return ChangeNickname(req)
    else:
        return UserProfile(req)

@login_required
def ChangePassword(req):
    """
    用户更新密码
    :param req:
    :return:
    """
    if req.method == "POST":
        data = json.loads(req.POST.get('data'))
        current_password = data['current_password']
        new_password = data['new_password']
        userprofile_set = models.UserProfile.objects.filter(user_id=req.user.id)
        user_auth = authenticate(username=req.user.username,
                            password=current_password)
        data_send = {'auth_status': 0}
        if user_auth is not None and user_auth.is_active: # 认证成功
            userprofile_set.update(login_status=1)
            user_auth.set_password(new_password)
            user_auth.save()
            data_send['auth_status'] = 1
            data_send['url'] = '/auth/logout/'
        return HttpResponse(json.dumps({'data':data_send}))

@login_required
def UploadFile(req):
    """
    上传文件
    :param req:
    :return:
    """
    data = {'status':0}
    if req.method == "POST":
        allow_file_type = ['.png', '.jpg', '.gif']
        file_obj = req.FILES.get('file')        # get的key与 jQurey post中的数据key相同，form_data.append('file', $('#startUploadBtn')[0].files[0]);
        # print(file_obj.size, len(file_obj))
        # print(dir(file_obj))
        file_type = re.findall('.\w+$',file_obj.name)[0].lower()
        if file_obj and file_type in allow_file_type and len(file_obj) <= 2097152:       # 判断文件类型为允许的图片类型且文件大小不超过2M，这里的单位是字节，也可以用file_obj.size变量
            file_name = '%s%s%s' %(time.strftime('%Y%m%d%H%M%S',time.localtime(time.time())),random.randrange(10000,99999),file_type)
            db_ImageField_file_name = 'upload/user_image/%s' %(file_name)   # 组合 UserProfile表中head_portrait字段路径，该字段相当于 字符串字段

            # 保存文件，这里边传边写，小于2M的先保存到内存，其他的先保存到系统临时文件，然后再保存到目标文件
            with open('upload/user_image/%s' %(file_name),'wb+')  as fp:
                for chunk in file_obj.chunks():
                    fp.write(chunk)

            user_set = models.UserProfile.objects.filter(user_id=req.user.id)
            user_set.update(head_portrait=db_ImageField_file_name)
            data['status'] = 1
        else:
            data['status'] = 2
    return HttpResponse(json.dumps({'data':data}))

@login_required
def ChangeNickname(req):
    """
    修改昵称
    :param req:
    :return:
    """
    data_send = {'status':0}
    if req.method == "POST":
        data = req.POST.get('data')
        data = json.loads(data)
        if data['nickname_new']:
            user_set = models.UserProfile.objects.filter(user_id=req.user.id)
            user_set.update(name=data['nickname_new'])
            data_send['status'] = 1
    return HttpResponse(json.dumps({'data':data_send}))