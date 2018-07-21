#!/bin/bash
# check dns resolve

a_check="check.healthcheck.check"
nslookup_bin="/usr/bin/nslookup"

ns_ip=$1
port=53
timeout=2


function EchoHelp(){
    echo "use: ./check_dns_resolve.sh [ip] {port}"
    exit 1
}

if [ $2 ]; then
    port=$2
fi


if [ $ns_ip -a $a_check ]; then
    $nslookup_bin -timeout=${timeout} -port=$port $a_check $ns_ip > /dev/null
else
    EchoHelp

fi


exit $?

