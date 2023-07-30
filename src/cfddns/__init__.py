from .__config__ import CONFIG
from .__main__ import DDNS
from .__record_cache__ import records_cache

__all__ = ['__version__', 'CONFIG', 'DDNS', 'get_ipv4', 'get_ipv6', 'records_cache']
__version__ = '1.0.0'

get_ipv4 = DDNS.get_ipv4
get_ipv6 = DDNS.get_ipv6
