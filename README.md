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
 cucker/dns:latest
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
  ## PostgreSQL 11
  database：dns
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

### 系统架构示意图
![image](https://github.com/cucker0/file_store/blob/master/BindUI/%E5%9F%9F%E5%90%8D%E7%AE%A1%E7%90%86%E7%B3%BB%E7%BB%9F%E6%9E%B6%E6%9E%84.png)  


### 组件功能
* BindUI系统功能
    * 域名管理
        * 域名(zone)的增、查、改、删
        * 域名(zone)的启用/暂停
    * RR管理
        * RR的增、查、改、删
        * RR的启用/暂停
        * RR的批量导入/导出，支持Text和Excel格式
    * 用户管理
        * 新建用户
        * 用户的登录/注销
        * 用户自助管理（更改密码、头像）
* url-forwarder系统功能
    * HTTP URL的转发
        * 302显性URL
        * 301显性URL
        * 隐性URL
* BIND系统功能
    * 基于View的智能DNS解析
    * 基于bind-dlz的动态DNS解析

### 工作原理
* 为什么 BIND 可以从数据库中加载 zone 数据？

答：  
是因为 BIND 扩展了 DLZ 驱动。
  
DLZ 允许 BIND 直接从外部数据库检索 zone 数据。
  
DLZ 驱动程序支持多种数据库后端，包括 PostgreSQL、MySQL 和 LDA P等，其中 dlz-postgres 是连接 PostgreSQL 的驱动，dlz-mysql 是连接 MySQL 的驱动。

说明：DLZ是BIND 9的扩展驱动（从BIND 9.4.0开始默认集成了DLZ drivers[^1]，从BIND 9.17.19开始弃用DLZ drivers，从BIND 9.18开始移除DLZ drivers[^2]

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

basic字段的值是根据type类型和转发需求来确定，具体参考 "record 表设计" 的 basic 字段说明。

**WEB层：**  
URL转发器用于实现显性URL和隐性URL记录的转发。

显性URL记录使用URL重定向技术实现，包含302 URL重定向 和 301 URL重定向。

隐性URL记录使用 HTML iframe 内联框架技术实现。

## 数据模型设计
主要的表有 record、zone 表，record 表用于保存 RR 数据，zone 表用于保存 zone（区域）数据。

* zone 表设计

|序号 |字段        |数据类型    |长度  |默认值  |非空  |描述                       |
|:-- |:--         |:--       |:--  |:--  |:--  |:--                        |
|1   |id          | bigint   |     |     |是    | 主键，自动递增              |
|2   |zone_name   | varchar  |255  |     |是    | zone名称，域名。要求唯一     |
|3   |status      | varchar  |3    |'on' |是    | zone的启/停状态            |
|4   |create_time | datetime |     |     |     | 创建时间                   |
|5   |update_time | datetime |     |     |     | 最近更新时间                |
|6   |comment     | varchar  |255  |     |     | 备注                      |

说明：

(1) status字段的可选值：'on' 表示开启，'off' 表示停用。

(2) 为提高查询效率，可基于zone_name字段创建索引。

* record 表设计

|序号|字段            |数据类型   |长度 |默认值 |非空  |描述                              |
|:--|:--             |:--      |:-- |:--  |:--  |:--                                |
|1  |id              |bigint   |    |     |是   |主键，自动递增                    |
|2  |host            |varchar  |255 |'@'  |是   |主机                              |
|3  |type            |varchar  |64  |'A'  |是   |RR类型                            |
|4  |data            |varchar  |4096|     |是   |RR值                              |
|5  |ttl             |int      |    |     |     |TTL存活时间（秒）                 |
|6  |mx_priority     |int      |    |     |     |MX优先级（1-50），值越小越优先    |
|7  |refresh         |int      |    |     |     |SOA记录的同步间隔时间（秒）       |
|8  |retry           |int      |    |     |     |SOA记录的同步失败的重试时间（秒） |
|9  |expire          |int      |    |     |     |SOA记录的过期时间（秒）           |
|10 |minimum         |int      |    |     |     |SOA记录的最小默认TTL值（秒）      |
|11 |serial          |bigint   |    |     |     |SOA记录的序列号，范围[0, 4294967295][^3] |
|12 |mail            |varchar  |255 |     |     |域名负责人邮箱（SOA记录）         |
|13 |primary_ns      |varchar  |255 |     |     |SOA记录的主DNS服务器              |
|14 |status          |varchar  |3   |'on' |是   |RR的启/停状态                     |
|15 |resolution_line |varchar  |32  |'0'  |是   |解析线路标识                      |
|16 |basic           |int      |    |0    |是   |其他信息                          |
|17 |associate_rr_id |bigint   |    |     |     |关联record的id                    |
|18 |zone_id         |bigint   |    |     |是   |外键，关联zone的id                |
|19 |create_time     |datetime |    |     |     |创建时间                          |
|20 |update_time     |datetime |    |     |     |最近更新时间                      |
|21 |comment         |varchar  |255 |     |     |备注                              |

说明：

(1) type字段的常用可选项：
```text
CNAME：别名记录，给域名取别名。
AAAA：IPv6记录，将域名指向一个IPv6地址。
NS：委派DNS zone使用指定的权威DNS服务器。
MX：邮件交换记录，用于给域指定邮件服务器。
SRV：通用服务定位记录。用于查询指定服务的信息，如服务名、通信协议、域名、优先级、权重、服务端口等信息。
TXT：文本记录。用于保存描述性文本。
PRT：指向主机记录或别名记录的指针。常用于DNS反向解析，指将IP地址映射到主机记录。
CAA：DNS证书颁发机构授权，约束主机/域可接受的CA。
URI：可用于发布从主机名到URI的映射。
SOA：zone的起始授权记录，一个zone在同一个view下有且仅有一条SOA记录。用于指定有关DNS区域的权威信息，包括主DNS服务器、域名负责人的电子邮箱、zone序列号以及与刷新zone相关的几个计时器(refresh, retry, expire, minimum)。
```

(2) mail字段表示域名负责人的电子邮箱，在mail字段中使用“.”来替代电子邮件中的“@”字符。

(3) status字段的可选值：'on' 表示开启，'off' 表示停用。

(4) resolution_line字段表示解析线路标识，即代表一个ACL。这里需要预先定义各个ACL对应的resolution_line值，例如：
```text
'0'：其他网络(默认ACL)。
'cn'：中国网络。
'abroad'：国外网络。
'101'：中国电信网。
'102'：中国联通网络。
'103'：中国移动网络。
'104'：中国教育网络。
```
(5) basic字段用来表示其他信息，可选值和具体含义如下：
```text
0：可重复的非基础记录（基础记录是指SOA、NS记录，非基础记录是指除SOA、NS之外的记录；重复部分是指host、type、zone_id字段的组合，下面的与此相同）。
1：可重复的基础记录。
2：不可重复的基础记录。
3：被显性URL或者隐性URL记录所关联的RR，被关联的RR为CNAME记录。
200：隐性URL记录，type字段的值为'TXT'。
301：301重定向显性URL记录，type字段的值为'TXT'。
302：302重定向显性URL记录，type字段的值为'TXT'。
```
(6) associate_rr_id字段用于保存显性URL或隐性URL记录所关联的RR的id。

## 性能
* `BIND 9.12.1/BIND 9.12.4` + `PostgreSQL 11` QPS 可达 40000+.
* `BIND 9.16.36` + `MySQL 8` QPS 可达 1000+.
* `BIND 9.16.36` + `PostgreSQL 15` QPS 可达 1250+.

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
  
修改 {python安装根目录}/lib/python3.7/site-packages/django/db/backends/mysql/operations.py 146行，decode改为encode

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

[^1]: Mark Andrews. BIND 9.4.0 is now available [EB/OL]. [2023-04-18]. https://lists.isc.org/pipermail/bind-announce/2007-February/000210.html
[^2]: BIND 9 Significant Features Matrix [EB/OL]. [2023-04-18]. https://kb.isc.org/docs/aa-01310
[^3]: Serial Number Arithmetic [EB/OL]. [2023-06-23]. https://www.rfc-editor.org/rfc/rfc1982.txt#:~:text=The%20serial%20number%20in%20the,a%2032%20bit%20unsigned%20integer.