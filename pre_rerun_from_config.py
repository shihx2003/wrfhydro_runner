# -*- encoding: utf-8 -*-
'''
@File    :   pre_rerun_from_config.py
@Create  :   2025-04-04 19:48:11
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import yaml
import logging
from core import SimulationInfo, batch_instantiate, schedule_and_track_jobs

log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'pre_WRFHydro.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='a'),
        logging.StreamHandler()
    ]
) 

logger = logging.getLogger(__name__)
logger.debug("Main script started.")

error_id = ['pre_10021', 'pre_10022', 'pre_10072', 'pre_10073', 'pre_10074', 'pre_10111', 'pre_10112', 'pre_10113', 'pre_10114', 'pre_10115']

if __name__ == "__main__":
    sim_info = {
        'obj': 'pre_rerun_WRFHydro',
        'ROOT_DIR': './',
    }
    global_info = SimulationInfo(sim_info)
    global_info.creat_work_dirs()
    run_jobs = {}
    for job_id in error_id:
        config_path = os.path.join(global_info.ROOT_DIR, 'configs', f'{job_id}_Fuping_20190804inital_params_config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        print(config['set_params'])
        if list(config['set_params'].keys())==['RETDEPRTFAC']:
            val = round(config['set_params']['RETDEPRTFAC'], 4)
            temp_info = {
                'job_id': job_id,
                'period': {'start' : '2019-07-25', 'end' : '2019-08-17'},
                'event_no': 'Fuping_20190804',
                'set_params': {
                    'RETDEPRTFAC': val,
                },
            }
            run_jobs[job_id] = temp_info

        elif list(config['set_params'].keys())==['MANN']:
            val = config['set_params']['MANN']
            temp_info = {
                'job_id': job_id,
                'period': {'start' : '2019-07-25', 'end' : '2019-08-17'},
                'event_no': 'Fuping_20190804',
                'set_params': {
                    'MannN': val,
                },
            }
            run_jobs[job_id] = temp_info
        elif list(config['set_params'].keys())==['AXAJ']:
            val = config['set_params']['AXAJ']
            temp_info = {
                'job_id': job_id,
                'period': {'start' : '2019-07-25', 'end' : '2019-08-17'},
                'event_no': 'Fuping_20190804',
                'set_params': {
                    'AXAJ': val,
                },
            }
            run_jobs[job_id] = temp_info
    print(run_jobs)
    set_jobs = batch_instantiate(global_info, jobs=run_jobs, configs=None)
    schedule_and_track_jobs(set_jobs, max_num=5)