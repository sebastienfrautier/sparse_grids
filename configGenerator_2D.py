#!/usr/bin/python

import os
import csv
import time
import numpy as np
import subprocess

BASE_DIR = os.getcwd()      # if we get amibitous, this could become a command line param
output_folder = 'configs'   # this too

# these are defautls which are used if certain parameters aren't defined for generateConfig_2D
default_params = {'TEMP':2.5, 'V_x':1, 'V_y':1.5, 'DELTA_T':0.002, 'TIMESTEPS':1000, 'BLOCK_SIZE':100,
                  'CUTOFF_RADIUS':3, 'LINKED_CELL_SIZE_X':3, 'LINKED_CELL_SIZE_Y':3} 

def generateConfig_2D(params):
    with open('config2D_template.xml') as f:
        template = f.read()
    for param, val in default_params.items():
        if param in params.keys():
            val = params[param]
        template = template.replace(param, str(val))
    return template

def write_times(times, path = 'out.csv'):
    with open(path, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(times)
        
if __name__ == '__main__':
    
    times = []
    cutoff_radius_range = np.linspace(0,5,100)
    block_size_range = range(50,151, 5)
    params = {'CUTOFF_RADIUS':cutoff_radius_range}
    params = {'BLOCK_SIZE':block_size_range}
    
    path = os.path.join(BASE_DIR, output_folder)
    if not os.path.exists(path): os.mkdir(path)
    for param, param_range, in params.items():
        for val in param_range:
            config = generateConfig_2D({param:val})
            filename = reduce(lambda s, param: '{0}_{1}={2:0.4f}'.format(s, param, val), 
                              params, 'config2D') + '.xml'
            path = os.path.join(BASE_DIR, output_folder, filename)

            with open(path, 'w+') as f:
                f.write(config)

            start = time.time()
            res = subprocess.call(["./simplemd", os.path.join('..',path)])
            if res == 0:
                times.append((val, time.time() - start))
            else:
                times.append((val, 'NA'))
    write_times(times, path = '{0}_times.csv'.format(param))
