import functools
import json
import threading
import time

import logPPP
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from .__record_cache__ import records_cache


class DDNS:
    # 创建线程锁
    _LOCK = threading.Lock()
    # 创建定时任务调度器
    _SCHEDULER = BackgroundScheduler()

    def __init__(self, _conf: dict):
        self.interval = _conf['interval']
        self.api_token = _conf['api_token']
        self.zone_id = _conf['zone_id']
        self.dns_records = _conf['dns_records']

        self._init()

    def _init(self):
        # 初始化提示
        logPPP.info('CFDDNS', '服务正在初始化, 请稍后...')
        cache = records_cache(self.api_token, self.zone_id, self.dns_records)
        cache.init_records_cache()

    def _update_dns_record(self, _record_id, _dns_name, _rerecord_type, _record_content, _proxied=True):
        try:
            resp = requests.put(
                'https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}'.format(
                    self.zone_id, _record_id),
                json={
                    'type': _rerecord_type,
                    'name': _dns_name,
                    'content': _record_content,
                    'proxied': _proxied
                },
                headers={
                    'Authorization': 'Bearer ' + self.api_token,
                    'Content-Type': 'application/json'
                })
        except Exception as e:
            with DDNS._LOCK:
                logPPP.error('update_dns_record', e)
            return False
        if not json.loads(resp.text).get('success'):
            with DDNS._LOCK:
                logPPP.warning('update_dns_record', resp.text)
            return False
        return True

    def update_dns(self, i):
        ip = None
        if str.lower(i.get('ip_type')).strip() == 'ipv4':
            ip = DDNS.get_ipv4()
        elif str.lower(i.get('ip_type')).strip() == 'ipv6':
            ip = DDNS.get_ipv6()
        if ip is None or ip == '':
            with DDNS._LOCK:
                logPPP.warning('CFDDNS', '获取本机IP地址失败')
            return
        # 获取缓存
        record_key = i.get('dns_name') + str.lower(i.get('ip_type'))
        record = records_cache.get_record_by_key(record_key)
        if record is None:
            with DDNS._LOCK:
                logPPP.warning('CFDDNS', i.get('dns_name'), '未找到域名记录')
            return
        if record.get('content') == ip:
            with DDNS._LOCK:
                logPPP.info('CFDDNS', i.get('dns_name'), 'IP地址未发生变化')
            return
        if self._update_dns_record(record.get('id'), i.get('dns_name'), record.get('type'), ip, i.get('proxied')):
            # 更新record的content
            record['content'] = ip
            # 更新record的proxied
            record['proxied'] = i.get('proxied')
            # 更新缓存
            records_cache.update_records_cache(record_key, record)
            with DDNS._LOCK:
                logPPP.info('CFDDNS', i.get('dns_name'), '-', ip, 'cloudflare DNS 记录更新成功')

    #  创建定时任务
    def create_job(self):
        # 添加定时任务，指定使用线程池执行
        for i in self.dns_records:
            task = functools.partial(self.update_dns, i)
            DDNS._SCHEDULER.add_job(task, 'interval', seconds=self.interval, max_instances=self.dns_records.__len__())

    # 启动定时任务
    @classmethod
    def run(cls):
        cls._SCHEDULER.start()
        logPPP.info("cloudflare DDNS 服务已启动")
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            cls._SCHEDULER.shutdown()
            logPPP.info("cloudflare DDNS 服务已停止")

    # 获取本机IPV6地址
    @staticmethod
    def get_ipv6():
        try:
            resp = requests.get('https://ipv6.icanhazip.com/')
        except Exception as e:
            logPPP.error('get_ipv6', e)
            return None
        return resp.text.strip()

    # 获取本机IPV4地址
    @staticmethod
    def get_ipv4():
        try:
            resp = requests.get('https://ipv4.icanhazip.com/')
        except Exception as e:
            logPPP.error('get_ipv4', e)
            return None
        return resp.text.strip()
