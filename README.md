# BindUI

Bind web admin UI


# 依赖模块
django
Pillow
pymysql
IPy
xlrd
xlwt

# 注意
* mysql连接驱动改为 pymysql
```
报错：
执行python manager.py 相关操作报错：django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3.

解决方法：
* 在每个app目录的__init__.py文件添加下面的内容：
import pymysql
pymysql.install_as_MySQLdb()

* {python安装根目录}/lib/python3.7/site-packages/django/db/backends/mysql/base.py 注意下面这两行
if version < (1, 3, 3):
    raise ImproperlyConfigured("mysqlclient 1.3.3 or newer is required; you have %s" % Database.__version__)

```

# 操作页面
![image](https://github.com/cucker0/file_store/blob/master/BindUI/01.png)
![image](https://github.com/cucker0/file_store/blob/master/BindUI/02.png)
![image](https://github.com/cucker0/file_store/blob/master/BindUI/03.png)
![image](https://github.com/cucker0/file_store/blob/master/BindUI/3.2.png)
![image](https://github.com/cucker0/file_store/blob/master/BindUI/04.png)
![image](https://github.com/cucker0/file_store/blob/master/BindUI/05.png)
![image](https://github.com/cucker0/file_store/blob/master/BindUI/06.png)