# -*- encoding: utf-8 -*-
'''
@File    :   params_excel.py
@Create  :   2025-03-29 20:03:38
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import pandas as pd
import yaml

params_excel = r"G:\Desktop\毕业设计\实验设计\实验设计.xlsx"
params_df = pd.read_excel(params_excel, sheet_name='select_params')
print(params_df)
params_dict = {}
for _, row in params_df.iterrows():
    if row['param'] == 'SMCMAX':
        params_dict[row['param']] = {
            'name'    : ['smcmax', 'SMCMAX1'],
            'minValue': row['minValue'],
            'maxValue': row['maxValue'],
            'iniValue': row['iniValue'],
            'file'    : ['soil_properties.nc', 'hydro2dtbl.nc'],
            'adjust'  : row['adjust'],
            'description': row['description']
        }
    else:
        params_dict[row['param']] = {
            'name'    : row['name'],
            'minValue': row['minValue'],
            'maxValue': row['maxValue'],
            'iniValue': row['iniValue'],
            'file'    : row['file'],
            'adjust'  : row['adjust'],
            'description': row['description']
        }

yaml_string = yaml.dump(params_dict, default_flow_style=False, sort_keys=False)
with open(os.path.join(os.path.dirname(__file__), 'run_params.yaml'), 'w') as f:
    yaml.dump(params_dict, f, default_flow_style=False, sort_keys=False)