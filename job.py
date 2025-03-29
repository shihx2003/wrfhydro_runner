# -*- encoding: utf-8 -*-
'''
@File    :   job.py
@Create  :   2025-03-29 15:58:42
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib

from core.read_params import read_yaml, chan_param, nc_params

import os
import shutil
import yaml
import logging
import subprocess
from datetime import datetime
from core.read_params import read_yaml, chan_param, nc_params

class ModelRunner:
    def __init__(self, sim_info):
        """
        initialize the ModelRunner with simulation information.
        """
        self.job_id = sim_info['job_id']
        self.period = sim_info['period']
        self.event_no = sim_info['event_no']
        self.source_dir = sim_info['source_dir']
        self.desrin_dir = sim_info['desrin_dir']
        self.result_dir = sim_info['result_dir']

        self.model_params = sim_info['model_params']
        
        self.pbs_script = sim_info.get('pbs_script', 'Hydrojob.pbs')
        self.wrfhydrofrxst = sim_info.get('wrfhydrofrxst', 'frxst_pts_out.txt')
        self.pbs_id = None
        
    
    def save_config(self, config_dir):

        """
        """
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
                'source_dir': self.source_dir,
                'desrin_dir': self.desrin_dir,
                'result_dir': self.result_dir,
                'model_params': self.model_params,
                'pbs_script': self.pbs_script,
                'wrfhydrofrxst': self.wrfhydrofrxst
            }
            
            # Dump the config data to YAML file
            yaml.dump(config_data, file, default_flow_style=False)
            print(f"模型配置已保存到 {config_file}")




    def copy_files(self, destination_dir):
        """
        从源位置复制文件到指定的目标目录。

        :param destination_dir: 目标目录
        """
        if not os.path.exists(destination_dir):
            os.makedirs(destination_dir)

        for file in self.source_files:
            if os.path.exists(file):
                shutil.copy(file, destination_dir)
                print(f"文件 {file} 复制到 {destination_dir}")
            else:
                print(f"文件 {file} 不存在!")

    def adjust_parameters(self, new_params):
        """
        根据新参数调整模型配置。

        :param new_params: 新的模型参数字典
        """
        self.model_params.update(new_params)
        print(f"模型参数已更新: {new_params}")

    def submit_pbs_job(self, pbs_script):
        """
        提交PBS作业。

        :param pbs_script: PBS脚本文件路径
        :return: 作业ID
        """
        # 使用subprocess提交PBS作业
        try:
            result = subprocess.run(['qsub', pbs_script], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.job_id = result.stdout.strip()
                print(f"PBS作业提交成功，作业ID: {self.job_id}")
            else:
                print(f"PBS作业提交失败: {result.stderr}")
        except Exception as e:
            print(f"提交PBS作业时发生错误: {e}")

    def collect_results(self, result_dir):
        """
        收集模拟结果并保存到指定目录。

        :param result_dir: 结果存储目录
        """
        if self.job_id is None:
            print("请先提交PBS作业！")
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
        print(f"开始模拟时间区间: {self.simulation_time}")
        print(f"模拟的洪水场次: {self.flood_event}")
        print(f"使用的模型参数: {self.model_params}")
        
        # 模拟开始
        self.copy_files(self.run_files)
        
        # 模拟参数调整
        # 这里你可以根据需要调整模型参数
        # self.adjust_parameters(new_model_params)
        
        # 提交PBS作业
        pbs_script = "your_pbs_script.sh"  # PBS脚本路径
        self.submit_pbs_job(pbs_script)
        
        # 收集模拟结果
        self.collect_results(self.result_dir)



if __name__ == "__main__":
    # 示例模拟信息
    sim_info = {
        'job_id': 'job_001',
        'period': '2025-01-01 to 2025-01-10',
        'event_no': 1,
        'source_dir': '/path/to/source',
        'desrin_dir': '/path/to/desrin',
        'result_dir': '/path/to/results',
        'model_params': {
            'slope': 0.1,
            'smcmax': 0.2,
            'MannN': 0.03
        }
    }

    # 创建模型运行实例并运行
    model_runner = ModelRunner(sim_info)
    model_runner.save_config('/path/to/config')