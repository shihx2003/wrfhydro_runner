# -*- encoding: utf-8 -*-
'''
@File    :   adjust_parms.py
@Create  :   2025-03-22 15:35:23
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import logging
import numpy as np
import xarray as xr


logger = logging.getLogger(__name__)

#################
# # Configure logging to output to the console (terminal)
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
#     handlers=[
#         logging.FileHandler('main.log'),
#         logging.StreamHandler()
#     ]
# )
#################


PRECISION = 1e-6

def adjust_value(info, ds):
    '''
    Adjust the parameter in the dataset based on the information in the dictionary
    Decide how to adjust the parameters.
    
    Parameters: 
    ----------
    info: dict
        A dictionary containing the information about the parameter to adjust
        NOTE: contains the sigal parameter, 
            e.g. {'name': 'slope', 'value': 0.5, 'adjust': 'replace'}
        
    ds: xarray.Dataset
        The dataset containing the parameter to adjust
    
    Returns:
    ----------
    ds: xarray.Dataset
        The dataset with the adjusted parameter
    '''

    exit_code = None
    ds = ds.copy(deep=True)
    param_name = info['name']
    param_value = info['value']
    param_adjust = info['adjust']

    c_max = ds[param_name].max().item()
    c_min = ds[param_name].min().item()

    logger.info(f"Adjusting parameter {param_name} with value {param_value} and adjust method {param_adjust}")
    logger.info(f"Parameter {param_name} has a maximum value of {c_max} and a minimum value of {c_min}")
    logger.info(f"Starting parameter adjustment")

    if param_adjust == 'replace':
        ds[param_name].values[:] = param_value
        
        # fix bug: if the parameter is negative, the max and min values are swapped
        if param_value >= 0:
            a_max = ds[param_name].max().item()
            a_min = ds[param_name].min().item()
        else:
            a_max = ds[param_name].min().item()
            a_min = ds[param_name].max().item()

        if (a_max - param_value) < PRECISION and (param_value - a_min) < PRECISION:
            logger.info(f"New max value is {a_max} and new min value is {a_min}")
            logger.info(f"Parameter {param_name} adjusted successfully to {param_value}")
            exit_code = 1
            return ds, exit_code
        else:
            exit_code = 0
            logger.error(f"Parameter {param_name} adjustment failed, current max value is {a_max} and min value is {a_min}.")
            logger.error(f"Exiting process [adjust_value]")
            return None, exit_code
    
    elif param_adjust == 'scale':
        ds[param_name] = ds[param_name] * param_value

        # fix bug: if the parameter is negative, the max and min values are swapped
        if param_value >= 0:
            a_max = ds[param_name].max().item()
            a_min = ds[param_name].min().item()
        else:
            a_max = ds[param_name].min().item()
            a_min = ds[param_name].max().item()

        if (a_max - c_max * param_value) < PRECISION and (c_min * param_value - a_min) < PRECISION:
            logger.info(f"New max value is {a_max} and new min value is {a_min}")
            logger.info(f"Parameter {param_name} adjusted successfully to {param_value}")
            exit_code = 1
            return ds, exit_code
        else:
            exit_code = 0
            logger.error(f"Parameter {param_name} adjustment failed, current max value is {a_max} and min value is {a_min}.")
            logger.error(f"Exiting process [adjust_value]")
            return None, exit_code
    else:
        exit_code = 0
        logger.error(f"Adjustment method {param_adjust} not recognized.")
        logger.error(f"Exiting process [adjust_value]")
        return None, exit_code


def select_nc(paraminfo, dsdict):
    '''
    Select the netCDF file to adjust
    Decide which netCDF file to adjust based on the information in the dictionary

    Parameters:
    ----------
    paraminfo: dict
        A dictionary containing the information about the parameter to adjust
        NOTE: contains the signal parameter but may not in the same file,
            e.g. {'name': ['smcmax', 'SMCMAX1'], 'value': 0.5, 'file': ['soil_properties.nc', 'hydro2dtbl.nc'], 'adjust': 'scale'}
    
    dsdict: dict
        A dictionary containing the xarray dataset to adjust

    '''

    exit_code = None
    dsdict = dsdict.copy()
    names = paraminfo['name']
    files = paraminfo['file']
    value = paraminfo['value']
    adjust = paraminfo['adjust']
    
    logger.info(f"names: {names}, files: {files}, value: {value}, adjust: {adjust}")

    for name, file in zip(names, files):
        if file in dsdict:
            logger.info(f"Found file {file} for parameter {name}")
            ds = dsdict[file]
            c_info = {
                'name': name,
                'value': value,
                'adjust': adjust
            }
            ds_adjusted, exit_code = adjust_value(c_info, ds)
            
            if exit_code == 1:
                dsdict[file] = ds_adjusted
                logger.info(f"File {file} adjusted successfully.")
            else:
                exit_code = 0
                logger.error(f"File {file} adjustment failed.")
                return dsdict, exit_code
        else:
            exit_code = 0
            logger.error(f"File {file} not found in the dataset.")
            logger.error(f"Exiting process [select_nc]")
            return dsdict, exit_code
        
    return dsdict, exit_code


def read_nc(dir):
    '''
    Read the netCDF file
    Read the netCDF file and return the dataset
    '''
    nc_files = ['Fulldom_hires.nc0', 'hydro2dtbl.nc0', 'soil_properties.nc0', 'GWBUCKPARM.nc0']
    
    dsdict = {}
    for file in nc_files:
        try:
            ds = xr.open_dataset(os.path.join(dir, file))
            logger.info(f"File {file[:-1]} read successfully.")
            dsdict[file[:-1]] = ds
        except Exception as e:
            logger.error(f"Failed to read file {file}.")
            logger.error(f"Error: {e}")
            logger.error(f"File {file} not found in the directory {dir}.")
            logger.error(f"Exiting process [read_nc]")
            return None
        
    return dsdict


def save_nc(dsdict, dir):
    '''
    Save the netCDF file
    Save the dataset to the netCDF file
    '''
    for file, ds in dsdict.items():
        try:
            ds.to_netcdf(os.path.join(dir, file))
            if not os.path.exists(dir):
                os.makedirs(dir)
                logger.info(f"Created output directory {dir}")
            file_path = os.path.join(dir, file)
            if os.path.exists(file_path):
                logger.info(f"File {file} saved successfully.")
            exit_code = 1
            
        except:
            exit_code = 0
            logger.error(f"Failed to save file {file}.")
            logger.error(f"Exiting process [save_nc]")

    return exit_code

def nc_params(params, indir, outdir):
    '''
    Adjust the parameters in the dictionary based on the values in the xarray dataset
    Decide how to adjust multiple parameters.

    Parameters:
    ----------
    params: list
        A list of dictionaries containing the information about the parameters to adjust
        NOTE: contains the signal parameter, 
            e.g. [{'name': 'slope', 'value': 0.5, 'adjust': 'replace'}, {'name': 'slope', 'value': 0.5, 'adjust': 'replace'}]
    
    indir: str
        The directory containing the netCDF files to adjust
    
    outdir: str
        The directory to save the adjusted

    Returns:
    ----------
    exit_code: int
        A code indicating whether the process was successful
        1: successful
        0: failed
    '''

    logger.info(f"Reading netCDF files.")
    dsdict = read_nc(indir)
    if dsdict is None:
        return None
    for param in params:
        dsdict, exit_code = select_nc(param, dsdict)
        if exit_code == 1:
            logger.info(f"Parameters {param['name']} adjusted successfully.")
        else:
            exit_code = 0
            logger.error(f"Parameter adjustment failed.")
            logger.error(f"Exiting process [adjust_parms]")
            return exit_code
    logger.info(f"All parameters adjusted successfully.")

    logger.info(f"Saving adjusted parameters to netCDF files.")
    exit_code = save_nc(dsdict, outdir)
    if exit_code == 1:
        logger.info(f"netCDF files saved successfully.")
        logger.info(f"Exiting process [adjust_parms]")
        return exit_code
    else:
        logger.error(f"Failed to save netCDF files.")
        logger.error(f"Exiting process [adjust_parms]")
        return exit_code

def chan_param(params, indir, outdir):
    '''
    Adjust the CHANPARM.TBL file based on the value of the parameter
    '''
    exit_code = None
    if params is None:
        params = {}
    
    # Default values for missing keys
    default_params = {
        'Bw': 1.0,
        'HLINK': 1.0,
        'ChSSlp': 1.0,
        'MannN': 1.0
    }
    
    # Use default values if keys are missing
    for key in default_params:
        if key not in params:
            params[key] = default_params[key]
            logger.info(f"Parameter {key} not provided, using default value: 1.0")
    
    try:
        input_file = os.path.join(indir, "CHANPARM.TBL.temp")
        output_file = os.path.join(outdir, "CHANPARM.TBL")

        logger.info(f"Reading CHANPARM.TBL.temp file.")
        with open(input_file, 'r', encoding='utf-8') as f, open(output_file, 'w', encoding='utf-8') as w:

            for _ in range(3):
                line = f.readline()
                w.write(line)

            for num in range(1, 11):
                line = f.readline()
                if not line:
                    break
                
                linestr = line.split(',')
                logger.info(f"Reading line {num}: {linestr}")
                logger.info(f"params Bw: {params['Bw']}, HLINK: {params['HLINK']}, ChSSlp: {params['ChSSlp']}, MannN: {params['MannN']}")
                strl = [
                    int(linestr[0]),
                    float(linestr[1]) * params['Bw'],
                    float(linestr[2]) * params['HLINK'],
                    float(linestr[3]) * params['ChSSlp'],
                    float(linestr[4]) * params['MannN']
                ]
                data = f"{strl[0]},{strl[1]:8.3f},{strl[2]:8.3f},{strl[3]:8.3f},{strl[4]:8.3f}\n"
                logger.info(f"Adjusting line {num}: {data[:-1]}")
                w.write(data)
        exit_code = 1
        logger.info("Parameter CHANPARM.TBL adjusted successfully.")
        return exit_code
    except:
        exit_code = 0
        logger.error("Failed to adjust CHANPARM.TBL.")
        logger.error("Exiting process [chan_param]")
        return exit_code 


if __name__ == '__main__':
    pam = [
        {'name': ['slope'], 'file': ['soil_properties.nc'], 'value': 0.5, 'adjust': 'replace'}, 
        {'name': ['smcmax','SMCMAX1'], 'file': ['soil_properties.nc','hydro2dtbl.nc'], 'value': 0.5, 'adjust': 'scale'}
     ]
    indir = 'F:/Haihe/Run/control_run/Domain_def'
    outdir = 'F:/Haihe/Run/control_run/Domain'
    # exit_code = nc_params(pam, indir, outdir)
    chan_pam = {'Bw': 0.5, 'HLINK': 0.5, 'ChSSlp': 0.5, 'MannN': 0.5}
    exit_code = chan_param(chan_pam, indir, outdir)
    
    if exit_code == 1:
        logger.info("Process completed successfully.")
    else:
        logger.error("Process failed.")

