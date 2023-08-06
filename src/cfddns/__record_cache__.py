import json
import threading

import logPPP
import requests


class records_cache:
    _RECORDS = {}
    _LOCK = threading.Lock()

    def __init__(self, api_token, zone_id, dns_records):
        self.api_token = api_token
        self.zone_id = zone_id
        self.dns_records = dns_records

    def init_records_cache(self):
        for i in self.dns_records:
            try:
                resp = requests.get(
                    'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(self.zone_id),
                    headers={
                        'Authorization': 'Bearer ' + self.api_token,
                        'Content-Type': 'application/json'
                    })
                if resp.status_code == 200:
                    # 如果请求失败，抛出异常
                    if not json.loads(resp.text).get('success'):
                        err_str = resp.text.replace('\n', '').replace('\r', '').strip()
                        logPPP.debug('get_record', err_str)
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
                            self.update_records_cache(dns_name + ip_type, domain)
                            break
            except Exception as e:
                logPPP.debug('init_records_cache', e)
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
