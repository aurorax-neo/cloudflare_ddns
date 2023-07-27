import json

import logPPP
import requests


class DDNS:
    def __init__(self, api_token, zone_id):
        self.api_token = api_token
        self.zone_id = zone_id

    def get_record(self, _dns_name):
        try:
            resp = requests.get(
                'https://api.cloudflare.com/client/v4/zones/{}/dns_records'.format(self.zone_id),
                headers={
                    'Authorization': 'Bearer ' + self.api_token,
                    'Content-Type': 'application/json'
                })
        except Exception as e:
            logPPP.error('get_record', e)
            return None
        if not json.loads(resp.text).get('success'):
            logPPP.warning('get_record', resp.text)
            return None
        domains = json.loads(resp.text).get('result')
        for domain in domains:
            if _dns_name == domain.get('name'):
                return domain
        return None

    def update_dns_record(self, _record_id, _dns_name, _rerecord_type, _record_content, _proxied=True):
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
            logPPP.error('update_dns_record', e)
            return False
        if not json.loads(resp.text).get('success'):
            logPPP.warning('update_dns_record', resp.text)
            return False
        return True

    # 获取本机IPV6地址
    @staticmethod
    def get_ipv6():
        try:
            resp = requests.get('http://v6.ipv6-test.com/api/myip.php')
        except Exception as e:
            logPPP.error('get_ipv6', e)
            return None
        return resp.text.strip()

    # 获取本机IPV4地址
    @staticmethod
    def get_ipv4():
        try:
            resp = requests.get('http://v4.ipv6-test.com/api/myip.php')
        except Exception as e:
            logPPP.error('get_ipv4', e)
            return None
        return resp.text.strip()
