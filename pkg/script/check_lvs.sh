#!/bin/bash

servicename="lvs"
showname="lvs"
pid="lvs"
status="${showname}_failed"
success_status="${showname}_success"

function CheckPs(){
    local ret=`ip add show |grep -E "172.16.12.29" |wc -l`
    echo $ret
}

if [ $(CheckPs) == 0 ]; then
    service $servicename start
    sleep 1
    if [ $(CheckPs) != 0 ]; then
        status=$success_status
    fi

else
    status=$success_status
fi

echo $status

