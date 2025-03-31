# -*- encoding: utf-8 -*-
'''
@File    :   job.py
@Create  :   2025-03-29 15:58:42
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import libraries
import os
import shutil
import yaml
import logging
import subprocess
from datetime import datetime
from core import chan_param, nc_params, read_params

logger = logging.getLogger(__name__)
# Configure logging
def setup_logging(level=logging.INFO):
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    if root_logger.handlers:
        root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    return root_logger
setup_logging()

class SimulationInfo:
    def __init__(self, sim_info):
        """
        Initialize the SimulationInfo object with simulation information.
        """
        self.obj = sim_info['obj']
        self.ROOT_DIR = sim_info['ROOT_DIR']
        self.run_source_dir = os.path.join(self.ROOT_DIR, sim_info.get('run_source_dir','run_source'))
        self.run_dir = os.path.join(self.ROOT_DIR, sim_info.get('run_dir','run'))
        self.result_dir = os.path.join(self.ROOT_DIR, sim_info.get('result_dir','result'))
        self.config_dir = os.path.join(self.ROOT_DIR, sim_info.get('config_dir','config'))
        self.params_yaml = os.path.join(self.ROOT_DIR, sim_info.get('params_yaml','param/run_params.yaml'))

        with open(self.params_yaml, 'r', encoding='utf-8') as file:
            self.params_info = yaml.safe_load(file)
        logger.info(f"Parameters information loaded from {self.params_yaml}")

    def creat_work_dirs(self):
        """
        Check if required directories exist, create them if they don't.
        """
        dirs_to_check = [self.run_dir, self.result_dir, self.config_dir]
            
        for directory in dirs_to_check:
            if not os.path.exists(directory):
                logger.info(f"Directory {directory} does not exist. Creating...")
                try:
                    os.makedirs(directory)
                    logger.info(f"Created directory: {directory}")
                except Exception as e:
                    logger.error(f"Failed to create directory {directory}: {e}")
                    raise
            else:
                logger.debug(f"Directory exists: {directory}")

class ModelRunner:
    def __init__(self, sim_info, run_info=None, config=None):
        """
        initialize the ModelRunner with simulation information.
        """
        # Determine initialization source (sim_info dictionary or config file)
        if run_info is not None:
            # Initialize from sim_info dictionary
            self.job_id = run_info['job_id']
            self.period = run_info['period']
            self.event_no = str(run_info['event_no'])

            self.run_source_dir = sim_info.run_source_dir
            self.run_dir = sim_info.run_dir
            self.result_dir = sim_info.result_dir
            self.config_dir = sim_info.config_dir

            self.raw_run_dir = os.path.join(self.run_source_dir, self.event_no)

            self.params_info = sim_info.params_info
            self.set_params = run_info['set_params']
            self.pbs_script = run_info.get('pbs_script', 'Hydrojob.pbs')
            self.wrfhydrofrxst = run_info.get('wrfhydrofrxst', 'frxst_pts_out.txt')

        elif config is not None:
            # Initialize from config file
            with open(config, 'r', encoding='utf-8') as file:
                config_self = yaml.safe_load(file)
            
            self.job_id = config_self['job_id']
            self.period = config_self['period']
            self.event_no = config_self['event_no']
            self.raw_run_dir = config_self['raw_run_dir']
            self.run_dir = config_self['run_dir']
            self.result_dir = config_self['result_dir']
            self.set_params = config_self['set_params']
            self.pbs_script = config_self.get('pbs_script', 'Hydrojob.pbs')
            self.wrfhydrofrxst = config_self.get('wrfhydrofrxst', 'frxst_pts_out.txt')
        else:
            raise ValueError("Either sim_info or config must be provided")
            
        # Common initialization
        self.pbs_id = None
        self.job_dir = None
    
    def save_config(self, config_dir=None):
        """
        """
        if config_dir is None:
            config_dir = self.config_dir
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        config_name = self.job_id + '_config.yaml'
        config_file = os.path.join(config_dir, config_name)

        with open(config_file, 'w', encoding='utf-8') as file:
            # Create a dictionary with all relevant model parameters
            config_data = {
                'job_id': self.job_id,
                'period': self.period,
                'event_no': self.event_no,
                'raw_run_dir': self.raw_run_dir,
                'run_dir': self.run_dir,
                'result_dir': self.result_dir,
                'set_params': self.set_params,
                'pbs_script': self.pbs_script,
                'wrfhydrofrxst': self.wrfhydrofrxst,
                'pbs_id': self.pbs_id
            }
            
            # Dump the config data to YAML file
            yaml.dump(config_data, file, default_flow_style=False)
            logger.info(f"Job {self.job_id} configuration saved to {config_file}")
            
    def copy_folder(self):
        """
        """
        if not os.path.exists(self.raw_run_dir):
            logger.error(f"raw_run_dir {self.raw_run_dir} does not exist.")
            raise FileNotFoundError(f"raw_run_dir {self.raw_run_dir} does not exist.")
        
        i = 0
        job_dir = os.path.join(self.run_dir, self.job_id)
        while os.path.exists(job_dir):
            logger.warning(f"desrin_dir {job_dir} already exists. Choose a new directory.")
            i += 1
            job_dir = os.path.join(self.run_dir, self.job_id) + f"_{i}"
            if i > 5:
                logger.error(f"Failed to create a new job directory after 5 attempts.")
                raise RuntimeError(f"Failed to create a new job directory after 5 attempts.")
            
        os.makedirs(job_dir)
        self.job_dir = job_dir
        logger.info(f"Copying {self.raw_run_dir} to {self.job_dir} ...")

        try:
            shutil.copytree(self.raw_run_dir, self.job_dir, dirs_exist_ok=True)
            logger.info(f"Copied {self.raw_run_dir} to {self.job_dir}")
        except Exception as e:
            logger.error(f"Error copying folder: {e}")
            raise RuntimeError(f"Error copying folder: {e}")

    def inital_params(self, new_params=None):
        """
        NOTE : nc_files = ['Fulldom_hires.nc0', 'hydro2dtbl.nc0', 'soil_properties.nc0', 'GWBUCKPARM.nc0']
        """
        if new_params is not None:
            self.set_params.update(new_params)
            logger.info(f"Model parameters updated: {self.set_params}")

        if self.job_dir is None:
            logger.error("Job directory not set. Please run copy_folder() first.")
            raise RuntimeError("Job directory not set. Please run copy_folder() first.")
        
        # set params
        set_nc_param = []
        set_chan_param = {}
        for key, value in self.set_params.items():
            if key == 'Bw' or key == 'HLINK' or key == 'ChSSlp' or key == 'MannN':
                set_chan_param[key] = value
            else:
                if key not in self.params_info:
                    logger.warning(f"Parameter {key} not found in params_info. Skipping.")
                    raise KeyError(f"Parameter {key} not found in params_info.")
                
                param_info = self.params_info[key]

                if isinstance(param_info['name'], list) and isinstance(param_info['file'], list):
                    pam = {
                        'name': param_info['name'],
                        'file': param_info['file'],
                        'value': value,
                        'adjust': param_info['adjust']
                    }
                elif isinstance(param_info['name'], str) and isinstance(param_info['file'], str):
                    pam = {
                        'name': [param_info['name']],
                        'file': [param_info['file']],
                        'value': value,
                        'adjust': param_info['adjust']
                    }
                else:
                    logger.error(f"Parameter {key} has inconsistent types for name and file.")
                    raise TypeError(f"Parameter {key} has inconsistent types for name and file.")
            set_nc_param.append(pam)
        raw_params_files = os.path.join(self.run_source_dir, 'params_files')

        ec_nc = nc_params(set_nc_param, raw_params_files, os.path.join(self.job_dir, 'DOMAIN'))
        ec_chan = chan_param(set_chan_param, raw_params_files, self.job_dir)

        logger.info(f'inital nc_params with exit code : {ec_nc}')
        logger.info(f'inital chan_params with exit code : {ec_chan}')

        if ec_nc == 1 and ec_chan == 1:
            logger.info("Model parameters initialized successfully.")
        else:
            logger.error("Model parameters initialization failed.")
            raise RuntimeError("Model parameters initialization failed.")

    def submit_pbs_job(self):
        """
        """
        pbs_script = os.path.join(self.job_dir, self.pbs_script)
        logger.info(f"Submitting PBS job with script: {pbs_script}")
        
        try:
            result = subprocess.run(['qsub', pbs_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.pbs_id = result.stdout.strip()
                logger.info(f"PBS job submitted successfully. Job ID: {self.job_id}. PBS ID: {self.pbs_id}")
            else:
                logger.error(f"Error submitting PBS job: {result.stderr.strip()}")
                raise RuntimeError(f"Error submitting PBS job: {result.stderr.strip()}")
        except Exception as e:
            logger.error(f"Exception occurred while submitting PBS job: {e}")
            raise RuntimeError(f"Exception occurred while submitting PBS job: {e}")

    def collect_results(self, result_dir):
        """
        收集模拟结果并保存到指定目录。

        :param result_dir: 结果存储目录
        """
        if self.job_id is None:
            print("请先提交PBS作业并获取作业ID。")
            return

        # 结果存储路径设置
        self.result_dir = result_dir
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        print(f"开始收集结果到 {result_dir} ...")
        # 模拟结果收集的代码，这里只做一个简单示例
        # 假设PBS作业的结果存储在特定目录中
        result_file = f"/home/ghh2/{self.job_id}_output.nc"  # 示例路径
        if os.path.exists(result_file):
            shutil.copy(result_file, result_dir)
            print(f"结果文件 {result_file} 已复制到 {result_dir}")
        else:
            print(f"没有找到结果文件 {result_file}")

    def run(self):
        """
        运行模型模拟过程。
        """
        self.collect_results(self.result_dir)



if __name__ == "__main__":
    sim_info = {
        'obj': 'example_obj',
        'ROOT_DIR': 'F:/Haihe/Run/wrfhydro_runner',
    }

    run_info = {
        'job_id': 'example_job',
        'period': {'start' : datetime(2020, 1, 1, 0), 'end' : datetime(2020, 1,2, 20)},
        'event_no': 20200801,
        'set_params': {
            'SMCMAX': 0.2,
            'SLOPE': 0.1,
            'MannN': 0.5
        },
        'pbs_script': 'Hydrojob.pbs',
        'wrfhydrofrxst': 'frxst_pts_out.txt'
    }


    sim_info = SimulationInfo(sim_info)
    sim_info.creat_work_dirs()
    model_runner = ModelRunner(sim_info, run_info)
    model_runner.save_config()
    model_runner.copy_folder()
    model_runner.inital_params()
    model_runner.submit_pbs_job()