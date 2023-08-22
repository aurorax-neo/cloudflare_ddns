import os
import sys

import confutilPPP
import psutil

import cfddns
from cfddns import CONFIG
from cfddns.__util__ import logger

BIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bin')


def OUTPUT_PID():
    # 获取当前目录的上层目录下的bin目录
    PID_FILE = os.path.join(BIN_DIR, 'PID.txt')
    try:
        # 判断是否存在PID文件
        if os.path.exists(PID_FILE):
            # 如果存在PID文件，读取PID文件
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
                # 判断PID是否在运行
                if psutil.pid_exists(pid):
                    logger.error(f'Another instance(PID: {pid}) is already running.')
                    exit(1)

        pid = os.getpid()
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
    except Exception as e:
        logger.error('PID', e)
        exit(1)


if __name__ == '__main__':
    OUTPUT_PID()
    config = confutilPPP.check_config(CONFIG)
    if config is not None:
        for i in config:
            cfddns.DDNS(i).create_job()
        cfddns.DDNS.run()
    else:
        logger.error('{} {}'.format('CFDDNS', '配置文件错误'))
        sys.exit(1)
