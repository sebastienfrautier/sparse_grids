#!/usr/bin/python

import os
import csv
import time
import numpy as np
import subprocess

BASE_DIR = os.getcwd()      # if we get amibitous, this could become a command line param
output_folder = 'configs'   # this too

# these are defautls which are used if certain parameters aren't defined for generateConfig_2D

def generateConfig_2D(params):
    defaults = {'TEMP':2.5, 'V_x':1, 'V_y':1.5, 'DELTA_T':0.002, 'TIMESTEPS':1000, 'BLOCK_SIZE':100,
                      'CUTOFF_RADIUS':3, 'LINKED_CELL_SIZE_X':3, 'LINKED_CELL_SIZE_Y':3} 
    with open('config2D_template.xml') as f: template = f.read()
    defaults.update(params)
    for param, val in defaults.items():
        template = template.replace(param, str(val))
    return template, defaults

def write_times(times, path = 'out.csv'):
    with open(path, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(times)
        
if __name__ == '__main__':
    path = os.path.join(BASE_DIR, output_folder)
    if not os.path.exists(path): os.mkdir(path)

    times = []
    param_space = {'CUTOFF_RADIUS':np.linspace(0.5, 1.5, 0.5), 'BLOCK_SIZE':range(85, 95, 5)}
    for param, param_range, in param_space.items():
        for val in param_range:
            config, params = generateConfig_2D({param:val})
            filename = reduce(lambda s, item: '{0}_{1}={2:0.4f}'.format(s, *item),
                              params.items(), 'config2D') + '.xml'

            path = os.path.join(BASE_DIR, output_folder, filename)
            with open(path, 'w+') as f: f.write(config)

            start = time.time()
            res = subprocess.call(["./simplemd", os.path.join('..',path)])
            dt = time.time() - start if res == 0 else 'NA'
            times.append((params, dt))
    write_times(times, path = '{0}_times.csv'.format('_'.join(param_space.keys())))
