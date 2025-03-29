# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Create  :   2025-03-22 16:07:52
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

from .adjust_params import chan_param, nc_params
from .read_params import read_params


# Export these functions directly for easier imports
__all__ = ['chan_param', 'nc_params', 'read_params']
