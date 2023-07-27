from .__main__ import DDNS

__all__ = ['__version__', 'DDNS', 'get_ipv4', 'get_ipv6']
__version__ = '1.0.0'

get_ipv4 = DDNS.get_ipv4
get_ipv6 = DDNS.get_ipv6
