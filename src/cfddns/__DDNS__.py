import functools
import json
import random
import sys
import threading
import time

import requests
from apscheduler.schedulers.background import BackgroundScheduler

from src.lib import logPPP
from .__record_cache__ import records_cache
from .__util__ import RETRY_CALLBACK


class DDNS:
    # 创建线程锁
    _LOCK = threading.Lock()
    # 创建定时任务调度器
    _SCHEDULER = BackgroundScheduler()
    # 任务的最大并发数
    _MAX_WORKERS = 1000
    # 初始化参数List
    _INIT_PARAMS = []

    def __init__(self, _conf: dict):
        self.interval = _conf['interval']
        self.api_token = _conf['api_token']
        self.zone_id = _conf['zone_id']
        self.dns_records = _conf['dns_records']

        self._init()

    def _init(self):
        args = (self.api_token, self.zone_id, self.dns_records)
        DDNS._INIT_PARAMS.append(args)

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
            if resp.status_code == 200:
                if json.loads(resp.text).get('success'):
                    return True
                with DDNS._LOCK:
                    err_str = resp.text.replace('\n', '').replace('\r', '').strip()
                    logPPP.logger.debug(err_str)
                raise Exception(err_str)
        except Exception as e:
            with DDNS._LOCK:
                logPPP.logger.debug(e)
            raise e

    def update_dns(self, i):
        try:
            if str.lower(i.get('ip_type')).strip() == 'ipv4':
                ip = RETRY_CALLBACK(DDNS.get_ipv4, _max_retries=5)
            elif str.lower(i.get('ip_type')).strip() == 'ipv6':
                ip = RETRY_CALLBACK(DDNS.get_ipv6, _max_retries=5)
            else:
                return 0
        except Exception:
            with DDNS._LOCK:
                logPPP.logger.warning('获取本机IP地址失败')
            return 1
        # 获取缓存
        record_key = i.get('dns_name') + str.lower(i.get('ip_type'))
        record = records_cache.get_record_by_key(record_key)
        if record is None:
            with DDNS._LOCK:
                logPPP.logger.warning('{} {}'.format(i.get('dns_name'), '未找到域名记录'))
            return 2
        if record.get('content') == ip:
            with DDNS._LOCK:
                logPPP.logger.debug('{} {}'.format(i.get('dns_name'), 'IP地址未发生变化'))
            return 3
        try:
            if RETRY_CALLBACK(self._update_dns_record, _record_id=record.get('id', 'None'),
                              _dns_name=i.get('dns_name', 'None'),
                              _rerecord_type=record.get('type', 'None'),
                              _record_content=ip,
                              _proxied=i.get('proxied', True)):
                # 更新record的content
                record['content'] = ip
                # 更新record的proxied
                record['proxied'] = i.get('proxied', True)
                # 更新缓存
                records_cache.update_records_cache(record_key, record)
                with DDNS._LOCK:
                    logPPP.logger.info('{} - {} {}'.format(i.get('dns_name'), ip, 'cloudflare DNS 记录更新成功'))
                return 4
        except Exception as e:
            with DDNS._LOCK:
                logPPP.logger.error('{} - {} {} {}'.format(i.get('dns_name'), ip, 'cloudflare DNS 记录更新失败', e))
            return 5

    #  创建定时任务
    def create_job(self):
        # 随机时间间隔
        if self.interval < 32:
            self.interval = 30
        seconds = random.randint(-8, 8) + self.interval
        # 添加定时任务，指定使用线程池执行
        for i in self.dns_records:
            task = functools.partial(self.update_dns, i)
            DDNS._SCHEDULER.add_job(task, 'interval', seconds=seconds,
                                    max_instances=DDNS._MAX_WORKERS,
                                    misfire_grace_time=self.interval)

    @staticmethod
    def update_cache_task():
        try:
            for i in DDNS._INIT_PARAMS:
                RETRY_CALLBACK(_callback_func=records_cache.init_records_cache,
                               _api_token=i[0], _zone_id=i[1], _dns_records=i[2])
        except Exception as e:
            raise e

    # 启动定时任务
    @classmethod
    def run(cls):
        # 初始化缓存
        try:
            # 初始化提示
            logPPP.logger.info('{} {}'.format('CFDDNS', '服务正在初始化, 请稍后...'))
            # 初始化缓存
            cls.update_cache_task()
            # 创建定时更新缓存任务
            DDNS._SCHEDULER.add_job(cls.update_cache_task, 'interval', seconds=30, max_instances=DDNS._MAX_WORKERS)
            logPPP.logger.info('{} {}'.format('CFDDNS', '服务初始化完成'))
        except Exception as e:
            logPPP.logger.error('{} {}'.format('CFDDNS', '缓存初始化失败', e))
            sys.exit(1)

        try:
            # 启动定时任务
            cls._SCHEDULER.start()
            logPPP.logger.info("cloudflare DDNS 服务已启动")
            while True:
                time.sleep(10)
        except (KeyboardInterrupt, SystemExit):
            cls._SCHEDULER.shutdown()
            logPPP.logger.info("cloudflare DDNS 服务已停止")
        finally:
            sys.exit(0)

    # 获取本机IPV6地址
    @staticmethod
    def get_ipv6():
        try:
            resp = requests.get('https://api6.ipify.org/')
            if resp.status_code == 200:
                return resp.text.strip()
            else:
                err_str = resp.text.replace('\n', '').replace('\r', '').strip()
                logPPP.logger.debug('{} {}'.format('get_ipv6', err_str))
                raise Exception(err_str)
        except Exception as e_:
            raise e_

    # 获取本机IPV4地址
    @staticmethod
    def get_ipv4():
        try:
            resp = requests.get('https://api4.ipify.org/')
            if resp.status_code == 200:
                return resp.text.strip()
            else:
                err_str = resp.text.replace('\n', '').replace('\r', '').strip()
                logPPP.logger.debug('{} {}'.format('get_ipv4', err_str))
                raise Exception(err_str)
        except Exception as e_:
            raise e_
