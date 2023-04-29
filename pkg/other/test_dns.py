#!/usr/bin/python
# DNS压力测试

from sys import argv
import random, time, os
import subprocess

# 帮助信息
USEAGE = """python {0} <option>

option:
    host    指定提供DNS解析服务的DNS服务器地址
    gen    生成 RR 样本文件
    --help, -h    打印帮助信息
""".format(argv[0])

# RR sample
rr = [
    'dns.zz.com A',
    'zz.com SOA',
    'free.zz.com A',
    'go.com MX',
    'kaka.go.com A',
    'liangxi.go.com CNAME',
    '10.100.240.133 PTR',
]

DNS_SERVER=argv[1]
TEST_COUNT = 3
# BASE_DIR = "/root/dns/"
BASE_DIR = "./dns/"
SPECS=[
    {'num': 1000, 'filename': '1000rr.txt'},
    {'num': 4000, 'filename': '4000rr.txt'},
    {'num': 8000, 'filename': '8000rr.txt'},
    {'num': 16000, 'filename': '16000rr.txt'},
]

def getFilePath(specs:dict) -> str:
    return "{0}{1}".format(BASE_DIR, specs['filename'])

def genCommand(filePath, dnsServer=DNS_SERVER) -> str:
    command = r'queryperf -d %s -s %s |grep "Queries per second"' % (filePath, dnsServer)
    return command

def queryperf(command:str) -> int:
    print('command: ' + command)
    p = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret_raw = p.stdout.read()  # 结果为 b'  Queries per second:   197.881168 qps\n'
    ret = str(ret_raw, encoding="utf-8")  # str
    print('ret: ' + ret)
    qps = ret.split()[3]
    return int(float(qps))

def stressTest() -> dict:
    msg = {'data': []}
    total = 0
    count = 0
    for i in SPECS:
        one_queryperf = {'spec': i['num'], 'ret': []}
        for j in range(TEST_COUNT):
            qps = queryperf(genCommand(getFilePath(i), DNS_SERVER))
            one_queryperf['ret'].append(qps)
            time.sleep(2)
        one_queryperf['avg'] = int(sum(one_queryperf['ret']) / len(one_queryperf['ret']) )
        total += sum(one_queryperf['ret'])
        count += len(one_queryperf['ret'])
        msg['data'].append(one_queryperf)
        time.sleep(3)
    msg['avg'] = int(total / count)
    return msg

def genRrSampleFile():
    if not os.path.exists(BASE_DIR):
        os.mkdir(BASE_DIR)

    for i in SPECS:
        with open(getFilePath(i), 'w+') as f:
            for i in range(i['num']):
                index = random.randint(0, len(rr) - 1)
                f.write(rr[index] + '\n')

def main():
    if len(argv) < 2 or argv[1] in ('--help', '-h'):
        print(USEAGE)
        exit(1)
    elif argv[1] == 'gen':
        genRrSampleFile()
    else:
        ret = stressTest()
        print(ret)

if __name__ == '__main__':
    main()