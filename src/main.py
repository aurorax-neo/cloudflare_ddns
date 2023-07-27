import functools
import os
import threading

import confutilPPP
import logPPP
from apscheduler.schedulers.background import BackgroundScheduler

import cfddns
from config import CONFIG

# 创建线程锁
logPPP_lock = threading.Lock()


def update_dns(i):
    ddns = cfddns.DDNS(i['api_token'], i['zone_id'])
    record = ddns.get_record(i['dns_name'])
    if record is None:
        with logPPP_lock:
            logPPP.warning('CFDDNS', i.get('dns_name'), '未找到域名记录')
        return
    ip = None
    if str.lower(i.get('ip_type')).strip() == 'ipv4':
        ip = cfddns.get_ipv4()
    elif str.lower(i.get('ip_type')).strip() == 'ipv6':
        ip = cfddns.get_ipv6()
    if ip is None or ip == '':
        with logPPP_lock:
            logPPP.warning('CFDDNS', '获取本机IP地址失败')
        return
    if record.get('content') == ip:
        with logPPP_lock:
            logPPP.info('CFDDNS', i.get('dns_name'), 'IP地址未发生变化')
        return
    if ddns.update_dns_record(record.get('id'), i.get('dns_name'), record.get('type'), ip, i.get('proxied')):
        with logPPP_lock:
            logPPP.info('CFDDNS', i.get('dns_name'), 'IP地址更新成功')


def OUTPUT_PID():
    pid = os.getpid()
    with open(os.path.join(os.getcwd(), 'PID.txt'), 'w') as f:
        f.write(str(pid))


def DDNS(_conf):
    # 创建定时任务调度器
    scheduler = BackgroundScheduler()

    # 添加定时任务，指定使用线程池执行
    for i in _conf:
        task = functools.partial(update_dns, i)
        scheduler.add_job(task, 'interval', seconds=i.get('interval'), max_instances=10)
    scheduler.start()
    OUTPUT_PID()
    logPPP.info("cloudflare DDNS 服务已启动")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logPPP.warning("cloud flare DDNS 服务停止。")
        scheduler.shutdown()


def main():
    conf = confutilPPP.check_config(CONFIG)
    if conf is None:
        logPPP.error('配置文件错误')
        return
    DDNS(conf)


if __name__ == '__main__':
    main()
