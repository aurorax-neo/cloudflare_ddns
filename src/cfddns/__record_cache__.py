import json
import threading

import requests

from src.lib import logPPP


class records_cache:
    _RECORDS = {}
    _LOCK = threading.Lock()

    def __init__(self):
        # 禁用实例化
        raise Exception('禁止实例化')

    @staticmethod
    def init_records_cache(_api_token, _zone_id, _dns_records):
        for i in _dns_records:
            try:
                resp = requests.get(
                    'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(_zone_id),
                    headers={
                        'Authorization': 'Bearer ' + _api_token,
                        'Content-Type': 'application/json'
                    })
                if resp.status_code == 200:
                    # 如果请求失败，抛出异常
                    if not json.loads(resp.text).get('success'):
                        err_str = resp.text.replace('\n', '').replace('\r', '').strip()
                        logPPP.logger.debug('{} {}'.format('get_record', err_str))
                        raise Exception(err_str)
                    # 如果请求成功，获取result
                    domains = json.loads(resp.text).get('result')
                    dns_name = i.get('dns_name')
                    ip_type = str.lower(i.get('ip_type'))
                    record_type = None
                    if ip_type == 'ipv4':
                        record_type = 'A'
                    elif ip_type == 'ipv6':
                        record_type = 'AAAA'
                    for domain in domains:
                        if dns_name == domain.get('name') and record_type == domain.get('type'):
                            records_cache.update_records_cache(dns_name + ip_type, domain)
                            break
            except Exception as e:
                logPPP.logger.debug('{} {}'.format('update_records_cache', e))
                raise e

    # 获取缓存
    @classmethod
    def get_records_cache(cls):
        with cls._LOCK:
            return cls._RECORDS.copy()

    # 获取缓存通过key
    @classmethod
    def get_record_by_key(cls, _key):
        with cls._LOCK:
            return cls._RECORDS.get(_key)

    # 更新缓存
    @classmethod
    def update_records_cache(cls, _key, _value):
        with cls._LOCK:
            cls._RECORDS[_key] = _value
