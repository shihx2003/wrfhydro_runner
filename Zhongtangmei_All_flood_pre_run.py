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

event_no = ['20110724', '20110825','20120721', '20160719', '20180707', '20190722', '20190804', '20200718', '20200823']

sim_info = {
    'obj': 'All_flood_test',
    'ROOT_DIR': '/public/home/Shihuaixuan/Run/Haihe_Run/Zhongtangmei_test/',
}

job_info = {
        'job_id': None,
        'period': 'Not Supported',
        'event_no': None,
        'basin' : 'Zhongtangmei',
        'set_params': {}
    }

global_info = SimulationInfo(sim_info)
global_info.creat_work_dirs()
params_info = global_info.params_info

run_jobs = {}
i=1
for event in event_no:
    job_info = job_info.copy()
    job_info['job_id'] = f'Test_Zhongtangmei_{i}'
    job_info['event_no'] = f'Zhongtangmei_{event}'
    run_jobs[job_info['job_id']] = job_info
    i+=1

run_jobs_path = os.path.join(global_info.ROOT_DIR, 'job/Test_Zhongtangmei.yaml')
if not os.path.exists(run_jobs_path):
    os.makedirs(os.path.dirname(run_jobs_path), exist_ok=True)
with open(run_jobs_path, 'w') as f:
    yaml.dump(run_jobs, f, default_flow_style=False)

set_jobs = batch_instantiate(global_info, jobs=run_jobs, configs=None)
schedule_and_track_jobs(set_jobs, max_num=5)