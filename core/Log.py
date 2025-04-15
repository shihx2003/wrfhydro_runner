# -*- encoding: utf-8 -*-
'''
@File    :   Log.py
@Create  :   2025-04-15 18:56:14
@Author  :   shihx2003
@Version :   1.0
@Contact :   shihx2003@outlook.com
'''

# here put the import lib
import os
import logging
from datetime import datetime

class Log:
    def __init__(self, name, logfile=None, level=logging.DEBUG):

        self.name = name 
        self.log = logging.getLogger(name)
        self.log.setLevel(level)

        formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

        if not os.path.exists('./logs'):
            os.makedirs('./logs')
        if logfile is None:
            logfile = name + '_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_handler = logging.FileHandler(f'./logs/{logfile}.log')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)

        self.log.addHandler(file_handler)
    
    def get_log(self):
        return self.log
    

if __name__ == '__main__':
    logger = Log('test').get_log()
