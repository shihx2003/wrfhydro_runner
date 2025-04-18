#!/bin/bash

source ~/anaconda3/etc/profile.d/conda.sh
conda activate wrf_env
echo "The environment is activated and script is running."
nohup python3 Sen_Fuping.py > ./Sen_Fuping.log 2>&1 &
echo "Python script is running in the background. Check the log file for output."
ps aux | grep Sen_Fuping.py
