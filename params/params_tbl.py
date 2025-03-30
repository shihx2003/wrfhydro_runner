# -*- encoding: utf-8 -*-
'''
@File    :   params_re.py
@Create  :   2025-03-22 15:14:23
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import yaml
import os
import pandas as pd

file = 'calib_params.tbl'
params_file = os.path.join(os.path.dirname(__file__), file)
df = pd.read_csv(params_file, skipinitialspace=True)
df.columns = df.columns.str.strip()
print(df.head())
df = df.drop(columns=['calib_flag'])
params_dict = {}
for _, row in df.iterrows():
    params_dict[row['parameter']] = {
        'name'    : row['parameter'],
        'minValue': row['minValue'],
        'maxValue': row['maxValue'],
        'iniValue': row['ini'],
        'file'    : '',
        'adjust'  : '',
        'description': ''
    }

# Print the dictionary to verify
yaml_string = yaml.dump(params_dict, default_flow_style=False, sort_keys=False)

# Optionally save to a yaml file
with open(os.path.join(os.path.dirname(__file__), f'{file[:-4]}.yaml'), 'w') as f:
    yaml.dump(params_dict, f, default_flow_style=False, sort_keys=False)