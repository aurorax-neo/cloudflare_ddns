import logging
import os
import sys
from logging import *

__all__ = ['__version__', 'logger', 'Config', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'NOTSET', 'FATAL',
           'WARN']
__version__ = '1.2.0'

_LOGGING_LEVEL = logging.INFO
_LOGGING_IS_OUTPUT_FILE = True
_LOGGING_IS_OUTPUT_SYS_STDOUT = True
_LOGGING_FILE = os.path.join(os.getcwd(), "log.log")
_LOGGER_NAME = os.path.splitext(os.path.basename(_LOGGING_FILE))[0]
_LOGGING_FMT = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d] - %(message)s'
_LOGGING_DATE_FMT = '%Y-%m-%d %H:%M:%S'


def _get_logger():
    log = logging.getLogger(_LOGGER_NAME)
    for h in log.handlers:
        h.close()
        log.removeHandler(h)
        del h
    log.handlers.clear()
    log.propagate = False
    log.setLevel(_LOGGING_LEVEL)

    if _LOGGING_IS_OUTPUT_SYS_STDOUT:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(logging.Formatter(_LOGGING_FMT, datefmt=_LOGGING_DATE_FMT))
        log.addHandler(ch)

    if _LOGGING_IS_OUTPUT_FILE:
        fh = logging.FileHandler(_LOGGING_FILE, encoding='utf-8')
        fh.setFormatter(logging.Formatter(_LOGGING_FMT, datefmt=_LOGGING_DATE_FMT))
        log.addHandler(fh)
    return log


# 日志句柄
logger = _get_logger()


def _auto_refresh_config(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        global logger
        logger = _get_logger()
        return result

    return wrapper


@_auto_refresh_config
def Config(logging_level=None, logging_is_output_file=None, logging_is_output_sys_stdout=None,
           logging_file=None, logger_name=None, logging_fmt=None, logging_date_fmt=None):
    global _LOGGING_LEVEL, _LOGGING_IS_OUTPUT_FILE, _LOGGING_IS_OUTPUT_SYS_STDOUT, _LOGGING_FILE, _LOGGER_NAME, _LOGGING_FMT, _LOGGING_DATE_FMT

    if logging_level is not None:
        _LOGGING_LEVEL = logging_level

    if logging_is_output_file is not None:
        _LOGGING_IS_OUTPUT_FILE = logging_is_output_file

    if logging_is_output_sys_stdout is not None:
        _LOGGING_IS_OUTPUT_SYS_STDOUT = logging_is_output_sys_stdout

    if logging_file is not None:
        _LOGGING_FILE = logging_file

    if logger_name is not None:
        _LOGGER_NAME = logger_name

    if logging_fmt is not None:
        _LOGGING_FMT = logging_fmt

    if logging_date_fmt is not None:
        _LOGGING_DATE_FMT = logging_date_fmt
