# -*- encoding: utf-8 -*-
'''
@File    :   read_params.py
@Create  :   2025-03-24 10:36:17
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib

import os
import yaml
import logging

logger = logging.getLogger(__name__)

########
# Configure logging to output to the console (terminal)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('main.log'),
        logging.StreamHandler()
    ]
)
#################



def read_yaml(filepath, paramlist):
    """
    Opens a YAML file and returns its contents as a Python dictionary.
        
    Args:
        file_path (str): Path to the YAML file
            
    Returns:
        dict: Contents of the YAML file
            
    Raises:
        FileNotFoundError: If the file doesn't exist
        yaml.YAMLError: If there's an error parsing the YAML
    """
    exit_code = None
    paramsdict = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            params = yaml.safe_load(file)
            if not params:
                logging.error(f"YAML file is empty: {filepath}")
                raise ValueError(f"YAML file is empty: {filepath}")
            for param in paramlist:
                if param not in params:
                    logging.error(f"Parameter {param} not found in YAML file: {filepath}")
                    raise ValueError(f"Parameter {param} not found in YAML file: {filepath}")
                else:
                    paramsdict[param] = params[param]
                    logging.info(f"Parameter {param} found in YAML file: {filepath}")
        return paramsdict
    except FileNotFoundError:
        logging.error(f"YAML file not found: {filepath}")
        raise
    except yaml.YAMLError as e:
            logging.error(f"Error parsing YAML file {filepath}: {e}")
            raise yaml.YAMLError(f"Error parsing YAML file {filepath}: {e}")

def read_params(file, paramlist):
    """
    
    """
    MannN = None
    paramsdict = read_yaml(file, paramlist)
    try:
        for param in paramlist:
            if param == 'MannN':
                MannN = paramsdict[param]
                logger.info(f"Parameter name {param} found in set")
                continue
            
            if not isinstance(paramsdict[param]['name'], list):
                logger.error(f"Parameter name {param} is not a list")
                logger.info(f"Parameter name {param} converted to list")
                paramsdict[param]['name'] = [paramsdict[param]['name']]

            if not isinstance(paramsdict[param]['file'], list):
                logger.error(f"Parameter file {param} is not a list")
                paramsdict[param]['file'] = [paramsdict[param]['file']]
                logger.info(f"Parameter file {param} converted to list")
        return paramsdict, MannN
    
    except KeyError as e:
        logger.error(f"KeyError: {e}")
        raise KeyError(f"KeyError: {e}")


if __name__ == '__main__':
    paramlist = ['slope', 'smcmax', 'MannN']
    dir = "F:\Haihe\Run\control_run\params"
    file = os.path.join(dir, 'calib_params.yaml')
    paramsdict, MannN = read_params(file, paramlist)
    print(paramsdict)
    print(MannN)