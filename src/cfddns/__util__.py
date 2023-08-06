import time


# 重试回调函数
def RETRY_CALLBACK(_callback_func, _max_retries=3, _retry_interval=1, *args, **kwargs):
    retries = 0
    while retries < _max_retries:
        try:
            return _callback_func(*args, **kwargs)
        except Exception as e_:
            retries += 1
            if retries < _max_retries:
                time.sleep(_retry_interval)
            else:
                raise e_
