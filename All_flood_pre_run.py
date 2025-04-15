# -*- encoding: utf-8 -*-
'''
@File    :   All_flood_test.py
@Create  :   2025-04-15 18:42:02
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import yaml
import logging
from core import SimulationInfo, batch_instantiate, schedule_and_track_jobs
from core import Log

log_dir = r'./logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'mian.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

event_no = ['20160718', '20190804', '20120721','20200717','20130811','20200801','20200824','20120621']
sim_info = {
    'obj': 'All_flood_test',
    'ROOT_DIR': './',
}

job_info = {
        'job_id': None,
        'period': 'Not Supported',
        'event_no': None,
        'set_params': {}
    }

global_info = SimulationInfo(sim_info)
global_info.creat_work_dirs()
params_info = global_info.params_info

run_jobs = {}
for event in event_no:
    job_info = job_info.copy()
    job_info['job_id'] = f'All_test_{event}'
    job_info['event_no'] = f'Fuping_{event}'

    run_jobs[job_info['job_id']] = job_info

run_jobs_path = os.path.join(global_info.ROOT_DIR, 'job/All_test.yaml')
if not os.path.exists(run_jobs_path):
    os.makedirs(os.path.dirname(run_jobs_path), exist_ok=True)
with open(run_jobs_path, 'w') as f:
    yaml.dump(run_jobs, f, default_flow_style=False)

set_jobs = batch_instantiate(global_info, jobs=run_jobs, configs=None)
schedule_and_track_jobs(set_jobs, max_num=5)