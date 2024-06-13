# BindUI

Bind web admin UI.

一款基于 BIND、DLZ、MySQL/PostgreSQL、Djano 的WEB可视化域名管理系统。

支持多线路智能解析（基于view实现的智能DNS）、批量导入/导出域名记录(RR)、支持常用的RR类型，支持显性URL、隐性URL记录的转发。

## 快速体验
```bash
docker run -d --name dns \
 --restart=always \
 -p 53:53/udp \
 -p 53:53/tcp \
 -p 127.0.0.1:953:953/tcp \
 -p 80:80/tcp \
 -p 8000:8000/tcp \
 cucker/dns:all-2.2
```

* Port Info
    ```
    EXPOSE 53/udp 53/tcp 953/tcp 80/tcp 8000/tcp 3306/tcp
    53/udp -> bind
    53/tcp -> bind
    953/tcp -> bind
    80/tcp -> url-forwarder
    8000/tcp -> BindUI
    3306/tcp -> MySQL
    ```

## 运行环境
```bash
Python 3.11
Django 4
MySQL 8 | MariaDB 10 | PostgreSQL 15 (任选一个)

```

## 依赖模块
```bash
django Pillow pymysql IPy xlrd xlwt
```

**安装依赖模块**  
```bash
pip3 install -r ./requirements.txt
```

## 初始化
```bash
cd <项目的根路径>
python3 manage.py migrate
python3 manage.py makemigrations
python3 manage.py migrate

// 创新 Django 超级用户，用于 WEB 登录
python3 manage.py createsuperuser
```

如果是非 初始化时，修改了表的设计，则运行下列命令合并表的变动
```bash
cd <项目的根路径>
python3 manage.py makemigrations
python3 manage.py migrate
``` 

## 系统架构
本系统包含3个项目，分别是BindUI、url-forwarder和BIND。BindUI是一个基于Django架构的WEB项目，负责域名管理的可视化图形界面操作；url-forwarder是一个基于Spring Boot架构的WEB项目，也是一个URL转发器，负责显性URL、隐性URL记录的转发；BIND是一个开源的DNS软件，负责DNS的解析。

url-forwarder 项目：https://gitee.com/cucker/url-forwarder

* 系统架构示意图
![image](https://github.com/cucker0/file_store/blob/master/BindUI/%E5%9F%9F%E5%90%8D%E7%AE%A1%E7%90%86%E7%B3%BB%E7%BB%9F%E6%9E%B6%E6%9E%84.png)  


## 操作页面
![image](https://github.com/cucker0/file_store/blob/master/BindUI/01.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/02.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/03.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/3.2.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/04.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/05.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/06.png)  

## 注意
### mysql连接驱动改为 pymysql
#### 报错1  
```text
执行python manager.py 相关操作报错：
django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3.
```

**解决方法**

./bindUI/settings.py 添加下面的配置
```bash
import pymysql
# 指定 pymysql 的版本。主要是要比 Django 要求的最低版本要大
pymysql.version_info = (11, 1, 0, "final", 0)
pymysql.install_as_MySQLdb()
```

#### 报错2
```text
AttributeError: 'str' object has no attribute 'decode'
```

**解决方法**
  
修改python安装根目录}/lib/python3.7/site-packages/django/db/backends/mysql/operations.py 146行，decode改为encode

```python
if query is not None:
    query = query.decode(errors='replace')
return query

```

改成
```python
if query is not None:
    query = query.encode(errors='replace')
return query
```
