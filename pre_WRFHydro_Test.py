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
import time
import numpy as np
from datetime import datetime, timedelta
import xarray as xr
from core import SimulationInfo, ModelRunner
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

def max_job(jobs, max_num):
    """
    Get the maximum job number from the jobs dictionary.
    """

    set_jobs = {}
    for job_id, job_info in jobs.items():
        set_jobs[job_id] = ModelRunner(global_info, jobs[job_id])
    
    job_ids = list(jobs.keys())
    waiting_id = list(jobs.keys())
    running_id = []
    finished_id = []
    error_id = []
    for job_id in job_ids:
        try:
            set_jobs[job_id].run()
            logger.info(f"Job {job_id} started.")
            waiting_id.remove(job_id)
            running_id.append(job_id)
            logger.info('waiting for 10 seconds...')
            time.sleep(10)
        except Exception as e:
            logger.error(f"Error running job {job_id}: {e}")
            waiting_id.remove(job_id)
            finished_id.append(job_id)
            error_id.append(job_id)
            continue
            
        while ((len(waiting_id) == 0 or len(running_id) >= max_num)) and len(running_id) > 0:
            logger.info(f"Current Running Job: {len(running_id)}")
            logger.info(f"Current Waiting Job: {len(waiting_id)}")
            logger.info(f"Current Finished Job: {len(finished_id)}")
            logger.info(f"Current Error Job: {len(error_id)}")
            logger.info('Waiting for running jobs to finish...')
            running_id , temp_finished = check_and_collect(running_id, set_jobs)
            finished_id.extend(temp_finished)
            logger.info("Waiting for running jobs to finish...")
            time.sleep(10)

    logger.info("All jobs have been finished.")
    logger.info(f"Error jobs: {error_id}")


def check_and_collect(running_id, set_jobs):
    """
    Check the status of running jobs and collect results if finished.
    """
    to_remove = []
    for job_id in running_id:
        try:
            set_jobs[job_id].check_pbs_job_status()
            if set_jobs[job_id].job_status == "C":
                logger.info(f"Job {set_jobs[job_id].job_id} completed successfully.")
                set_jobs[job_id].collect_frxst(set_jobs[job_id].result_dir)
                set_jobs[job_id].save_config()
                to_remove.append(job_id)

            elif set_jobs[job_id].job_status == "E":
                logger.error(f"Job {set_jobs[job_id].job_id} encountered an error.")
                set_jobs[job_id].collect_frxst(set_jobs[job_id].result_dir, '_error')
                set_jobs[job_id].save_config()
                to_remove.append(job_id)

            elif set_jobs[job_id].job_status == "R":
                logger.info(f"Job {set_jobs[job_id].job_id} is still running.")
            else:
                logger.info(f"Job {set_jobs[job_id].job_id} is in an unknown state.")

        except Exception as e:
            logger.error(f"Error checking job {job_id}: {e}")
            continue
    for job_id in to_remove:
        running_id.remove(job_id)
    return running_id, to_remove

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
    max_job(run_jobs, 5)
