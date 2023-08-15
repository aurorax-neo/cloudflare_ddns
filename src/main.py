import os
import sys

import cfddns
from cfddns import CONFIG
from cfddns.lib import logPPP, confutilPPP


def OUTPUT_PID():
    try:
        pid = os.getpid()
        with open(os.path.join(os.getcwd(), 'PID.txt'), 'w') as f:
            f.write(str(pid))
    except Exception as e:
        logPPP.error('PID', e)


if __name__ == '__main__':
    OUTPUT_PID()
    config = confutilPPP.check_config(CONFIG)
    if config is not None:
        for i in config:
            cfddns.DDNS(i).create_job()
        cfddns.DDNS.run()
    else:
        logPPP.error('{} {}'.format('CFDDNS', '配置文件错误'))
        sys.exit(1)
