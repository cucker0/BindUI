# BindUI

Bind web admin UI.

这是一款基于BIND和WEB的智能DNS域名管理系。使用BIND + DLZ + MySQL/PostgreSQL + Django + Spring Boot技术进行开发。
支持常用的DNS记录类型、多线路智能解析（基于view实现的智能DNS）、批量导入/导出域名记录(RR)，并额外扩展了对HTTP URL转发的显性URL、隐性URL记录的支持。
降低了域名的管理和使用成本，成为一款易用的企业级域名管理系统。

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

* BindUI Account Info
    ```bash
    url：http://<IP>:8000
    user：admin
    password：Dns123456!
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
* Database
  ```bash
  ## database：dns
  user2：'dns_wr'@'%'
  password：Ww123456!
  
  user3：'dns_r'@'%'
  password：Rr123456!
  ```
## 运行环境
```bash
Linux
Python 3.11
Django 4
JDK 17
Spring boot 3
MySQL 8 | MariaDB 10 | PostgreSQL 15 (任选一个)
Bind 9.12.1 | Bind 9.16.39 (任选一个)
```

## 系统部署
* 参考 [部署智能 DNS 域名管理系](https://www.yuque.com/cucker/udwka0/cdx5ec7do39ov1c1?singleDoc#)

## 手册
* [BindUI 智能 DNS 域名管理系使用文档](https://www.yuque.com/cucker/udwka0/emk0i5bcgfrcv4m9?singleDoc#)

## 系统架构、组件功能
本系统包含3个组件，分别是BindUI、url-forwarder 和 BIND。

* BindUI  
  BindUI 是一个基于 Django 架构的 WEB 项目，负责域名管理的可视化图形界面操作；
* url-forwarder  
url-forwarder 是一个 URL 转发器，一个基于 Spring Boot 架构的 WEB 项目，负责 显性 URL、隐性 URL 记录的转发。

url-forwarder 项目：https://gitee.com/cucker/url-forwarder
* BIND  
BIND 是一个开源的DNS软件，负责DNS的解析。

* **系统架构示意图**
![image](https://github.com/cucker0/file_store/blob/master/BindUI/%E5%9F%9F%E5%90%8D%E7%AE%A1%E7%90%86%E7%B3%BB%E7%BB%9F%E6%9E%B6%E6%9E%84.png)  


* **组件功能**
![image](https://github.com/cucker0/file_store/blob/master/BindUI/%E7%BB%84%E4%BB%B6%E5%8A%9F%E8%83%BD%E8%AE%BE%E8%AE%A1.png)

### 工作原理
* 为什么 BIND 可以从数据库中加载 zone 数据？

答：  
是因为 BIND 扩展了 DLZ 驱动。
  
DLZ 允许 BIND 直接从外部数据库检索 zone 数据。
  
DLZ 驱动程序支持多种数据库后端，包括 PostgreSQL、MySQL 和 LDA P等，其中 dlz-postgres 是连接 PostgreSQL 的驱动，dlz-mysql 是连接 MySQL 的驱动。

* 多线路智能DNS解析是如何实现的？

答：  
BIND 中可配置多个 view，一个线路配置一个 view。  
当配置了多个 view 时，则是按照配置文件中 view 的位置顺序从上往下逐个匹配，当客户的 IP 与 view 的 match-clients 子句所指定的 ACL 匹配时，则该客户IP与此view匹配，应用此 view，并停止匹配其他 view。

如果希望把一个view作为默认的view(当没有匹配到任何的view时，就应用默认的view。例如定义名为default的view)，则在配置文件中把该view放到所有view的后面。

**关于ACL**  
用户可以自定义 ACL， 一个 ACL 中可定义了若干个网络。

BIND 内置了4个ACL，分别是any、none、localhost 和 localnets ACL。


* 显性 URL、隐性 URL 是怎样工作的？

答：  
**DNS层：**  
一条显性URL 或 一条隐性URL记录都是由两条相关联的记录共同实现的。

一条是type字段为 'CNAME' 的记录（CNAME记录），主要用于查找URL转发器地址。data字段的值为URL转发器地址（URL转发服务器的A记录的FQDN值），该记录的basic字段值为3。

另一条是type字段为 'TXT' 的记录（TXT记录），主要用于保存要转发的目标HTTP URL。该记录的data字段的值为要转发的目标HTTP URL，associate_rr_id字段的值为关联的CNAME记录的id。

basic字段的值是根据type类型和转发需求来确定，如果是“302 URL重定向”，那么basic字段值为302；  
如果是“301 URL重定向”，那么basic值为301；  
如果是隐性URL，那么basic值为200。

**WEB层：**  
URL转发器用于实现显性URL和隐性URL记录的转发。

显性URL记录使用URL重定向技术实现，包含302 URL重定向 和 301 URL重定向。

隐性URL记录使用 HTML iframe 内联框架技术实现。


## 操作页面
![image](https://github.com/cucker0/file_store/blob/master/BindUI/01.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/02.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/03.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/3.2.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/04.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/05.png)  
![image](https://github.com/cucker0/file_store/blob/master/BindUI/06.png)  

## 注意
### mysql 连接驱动改为 pymysql
* 报错1  
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

* 报错2
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
