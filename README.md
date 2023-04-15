# BindUI

Bind web admin UI.

一款基于 BIND、DLZ、MySQL/PostgreSQL、Djano 的WEB可视化域名管理系统。

支持多线路智能解析（基于view实现的智能DNS）、批量导入/导出域名记录(RR)、支持常用的RR类型。


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

1. 在每个app目录的__init__.py文件添加下面的内容
    ```python
    import pymysql
    pymysql.install_as_MySQLdb()
    ```
2. {python安装根目录}/lib/python3.7/site-packages/django/db/backends/mysql/base.py 注释下面这两行
```python
if version < (1, 3, 3):
    raise ImproperlyConfigured("mysqlclient 1.3.3 or newer is required; you have %s" % Database.__version__)
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