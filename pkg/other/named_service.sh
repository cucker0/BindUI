#!/bin/sh
# 调整 named 线程 或 PostgreSQL 连接数据

#set -u
USEAGE="useage: $0 <CPU_NUM> [PG_CONN_NUM]"

ARG1=$1
CPU_NUM=$1
PG_CONN_NUM=$2
SERVICE_PATH=/usr/lib/systemd/system/named.service
VIEW_CONFIG_PATH=/etc/named/conf.d/default.conf

modifyFile() {
    # modify named.service file
    if [ ! ${CPU_NUM} ]; then
        sed -i "s#^ExecStart=.*#ExecStart=/usr/local/bind/sbin/named -n 1 -u named -c /usr/local/bind/etc/named.conf#" ${SERVICE_PATH}
    elif [ ${CPU_NUM} == 'auto' ]; then
        sed -i "s#^ExecStart=.*#ExecStart=/usr/local/bind/sbin/named -u named -c /usr/local/bind/etc/named.conf#" ${SERVICE_PATH}
    else
        sed -i "s#^ExecStart=.*#ExecStart=/usr/local/bind/sbin/named -n ${CPU_NUM} -u named -c /usr/local/bind/etc/named.conf#" ${SERVICE_PATH}
    fi

    # modify view config file
    if [ ${PG_CONN_NUM} ]; then
        sed -i "s#database \"postgres.*#database \"postgres ${PG_CONN_NUM}#" ${VIEW_CONFIG_PATH}
    fi

}

main() {
    if [[ ${ARG1} == "-h" || ${ARG1} == "--help" ]]; then
        echo "${USEAGE}"
        exit 0
    fi
    modifyFile
    systemctl daemon-reload
    systemctl restart named.service
}

main