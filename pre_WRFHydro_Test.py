# -*- encoding: utf-8 -*-
'''
@File    :   pre_WRFHydro_Test.py
@Create  :   2025-04-02 16:19:46
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import logging
import yaml
from core import SimulationInfo, batch_instantiate, schedule_and_track_jobs
import os

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

if __name__ == "__main__":
    
    # run_info = {
    #     'period': {'start' : '2019-07-25', 'end' : '2019-08-17'},
    #     'event_no': 'Fuping_20190804',
    # }

    sim_info = {
        'obj': 'pre_WRFHydro',
        'ROOT_DIR': './work_dir',
    }
    global_info = SimulationInfo(sim_info)
    global_info.creat_work_dirs()
    logger.info(f"root_dir: {global_info.ROOT_DIR}")
    params_info = global_info.params_info
    
    run_jobs = {}

    # set the default run
    default = {
        'job_id': 'pre_10000',
        'period': {'start' : '2019-07-25', 'end' : '2019-08-17'},
        'event_no': 'Fuping_20190804',
        'set_params': {},
    }
    run_jobs[default['job_id']] = default

    job_id_num = 10001
    for param, info in params_info.items():

        max_val = info['maxValue']
        ini_val = info['iniValue']
        min_val = info['minValue']

        val_000 = min_val
        val_025 = min_val + (max_val - min_val) * 0.25
        val_050 = min_val + (max_val - min_val) * 0.50
        val_075 = min_val + (max_val - min_val) * 0.75
        val_100 = max_val

        val_list = [val_000, val_025, val_050, val_075, val_100]
        for val in val_list:
            temp_info = {
                'job_id': f'pre_{job_id_num}',
                'period': {'start' : '2019-07-25', 'end' : '2019-08-17'},
                'event_no': 'Fuping_20190804',
                'set_params': {
                    param: val,
                },
            }
            run_jobs[temp_info['job_id']] = temp_info
            job_id_num += 1

    run_jobs_path = os.path.join(global_info.config_dir, 'run_jobs.yaml')
    with open(run_jobs_path, 'w') as f:
        yaml.dump(run_jobs, f, default_flow_style=False)

    logger.info(f"Total jobs {len(run_jobs)}")
    set_jobs = batch_instantiate(run_jobs, global_info)
    schedule_and_track_jobs(set_jobs, 5)
