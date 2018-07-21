#!/bin/bash

servicename="named"
showname="named"
pid="named"
status="${showname}_failed"
success_status="${showname}_success"

function CheckPs(){
    local ret=`pidof $pid | wc -l`
    echo $ret
}

if [ $(CheckPs) == 0 ]; then
    service $servicename restart
    sleep 1
    if [ $(CheckPs) != 0 ]; then
        status=$success_status
    fi

else
    status=$success_status
fi

echo $status
