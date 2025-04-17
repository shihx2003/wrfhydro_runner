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
from .WRFHydroJob import SimulationInfo, ModelRunner
from .RunningJobs import batch_instantiate, schedule_and_track_jobs


# Example simulation information
sim_info = {
        'obj': 'pre_rerun_WRFHydro',
        'ROOT_DIR': './',
    }
job_info = {
        'job_id': 'job_id',
        'period': {'start' : '2019-07-25', 'end' : '2019-08-17'},
        'event_no': 'Fuping_20190804',
        'set_params': {
        'RETDEPRTFAC': 0.1,
        'MannN': 0.01,
        }
    }

#
__all__ = ['chan_param', 
           'nc_params', 
           'read_params', 
           'SimulationInfo', 
           'ModelRunner',
           'batch_instantiate', 
           'schedule_and_track_jobs',
           ]
