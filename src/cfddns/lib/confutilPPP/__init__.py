from .__confutil__ import confutil
from .logPPP import *

__all__ = ['__version__', 'check_config']
__version__ = '1.2.2'

Config(logging_level=INFO, logging_is_output_file=True, logging_is_output_sys_stdout=True,
       logging_file='confutilPPP.log', )


def check_config(_object=None, _filename='config'):
    return confutil.check_config(_object, _filename)
