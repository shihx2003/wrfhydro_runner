# -*- encoding: utf-8 -*-
'''
@File    :   RunningJobs.py
@Create  :   2025-04-04 19:07:54
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import time
import logging
from .WRFHydroJob import SimulationInfo, ModelRunner

logger = logging.getLogger(__name__)

def batch_instantiate(sim_info:SimulationInfo, jobs:dict=None, configs:dict=None):
    """
    Instantiate multiple ModelRunner objects based on provided job information or configurations.

    Parameters
    ----------
    sim_info : SimulationInfo
        An instance of the SimulationInfo class containing simulation information.
    jobs : dict, optional
        Dictionary of job information to instantiate ModelRunner objects.
    configs : dict, optional
        Dictionary of configurations to instantiate ModelRunner objects.
        Format --> {'job_id' : config}
    """
    set_jobs = {}
    if jobs is not None:
        for job_id, job_info in jobs.items():
            set_jobs[job_id] = ModelRunner(sim_info, job_info=job_info, config=None)
    if configs is not None:
        for job_id, config in configs.items():
            set_jobs[job_id] = ModelRunner(sim_info, job_info=None, config=config)
    if jobs is None and configs is None:
        logger.error("No jobs or configs provided.")
        raise ValueError("No jobs or configs provided.")
    
    return set_jobs

def schedule_and_track_jobs(set_jobs:dict, max_num:int=5):
    """
    Get the maximum job number from the jobs dictionary.

    Parameters
    ----------
    set_jobs : dict
        Dictionary of jobs to be scheduled and tracked.
        Format --> {'job_id' : ModelRunner object}
    max_num : int, optional, default=5
    """

    job_ids = list(set_jobs.keys())
    waiting_id = list(set_jobs.keys())
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


def check_and_collect(running_id:list, set_jobs:dict):
    """
    Check the status of running jobs and collect results if finished. Current used in the schedule_and_track_jobs function.
    
    Parameters
    ----------
    running_id : list
        List of job IDs that are currently running.
    set_jobs : dict
        Dictionary of jobs to be checked.
        Format --> {'job_id' : ModelRunner object}

    Returns
    ----------
    running_id : list
        Updated list of job IDs that are still running.
    finished_id : list
        List of job IDs that have finished running.
    """
    to_remove = []
    for job_id in running_id:
        try:
            set_jobs[job_id].check_pbs_job_status()
            if set_jobs[job_id].job_status == "C":
                logger.info(f"Job {set_jobs[job_id].job_id} completed successfully.")
                set_jobs[job_id].collect_frxst(set_jobs[job_id].result_dir)
                set_jobs[job_id].cleanup()
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