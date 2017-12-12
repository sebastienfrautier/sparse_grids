#!/usr/bin/python

import os
import csv
import time
import numpy as np
import subprocess
import collections
import random
import sys

BASE_DIR = os.getcwd()      # if we get amibitous, this could become a command line param
output_folder = 'configs'   # this too

# these are defautls which are used if certain parameters aren't defined for generateConfig_2D

def generateConfig_2D(params):
    defaults = {'TEMP':2.5, 'V_x':1, 'V_y':1.5, 'DELTA_T':0.002, 'TIMESTEPS':1000, 'BLOCK_SIZE':100,
                      'CUTOFF_RADIUS':3, 'LINKED_CELL_SIZE_X':3, 'LINKED_CELL_SIZE_Y':3,'DOMAIN_SIZE':5,'MOL_X':2,'MOL_Y':2}
    with open('config2D_template.xml') as f: template = f.read()
    defaults.update(params)
    for param, val in defaults.items():
        template = template.replace(param, str(val))

    for k,v in defaults.items():
        print k,v
    return template, defaults

def write_times(times, path = 'out.csv'):
    with open(path, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(times)

if __name__ == '__main__':
    path = os.path.join(BASE_DIR, output_folder)
    if not os.path.exists(path): os.mkdir(path)

    times = []
    for i in range(0,int(sys.argv[1])):

        full_param_space = collections.OrderedDict({"MOL_X": np.linspace(20, 80, 100)
                                                        ,"MOL_Y": np.linspace(20, 80, 100)
                                                        , 'LINKED_CELL_SIZE_Y': np.linspace(1, 20, 100)
                                                        , 'LINKED_CELL_SIZE_X': np.linspace(1, 20, 100)
                                                        , 'CUTOFF_RADIUS': np.linspace(0, 20, 100)
                                                        , 'BLOCK_SIZE': range(2, 100)
                                                        , 'DOMAIN_SIZE': range(1, 100)})

        constrained_random_config = collections.OrderedDict({})

        for k, v in full_param_space.items():

            if k == 'BLOCK_SIZE':

                block_size_choice = random.choice(full_param_space[k])

                while (constrained_random_config['DOMAIN_SIZE'] % block_size_choice) != 0:
                    block_size_choice = random.choice(full_param_space[k])

                constrained_random_config[k] = block_size_choice

            elif k == 'CUTOFF_RADIUS':

                cutoff_radius_choice = random.choice(full_param_space[k])
                while (constrained_random_config['LINKED_CELL_SIZE_X'] < cutoff_radius_choice and constrained_random_config[
                    'LINKED_CELL_SIZE_Y'] < cutoff_radius_choice):
                    cutoff_radius_choice = random.choice(full_param_space[k])

                constrained_random_config[k] = cutoff_radius_choice

            else:
                constrained_random_config[k] = random.choice(full_param_space[k])


        for param,val in constrained_random_config.items():
            print param,val

            #config, params = generateConfig_2D({param:val})

        config, params = generateConfig_2D(constrained_random_config)
        filename = reduce(lambda s, item: '{0}_{1}={2:0.4f}'.format(s, *item),
                              params.items(), 'config2D') + '.xml'

        path = os.path.join(BASE_DIR, output_folder, filename)
        with open(path, 'w+') as f: f.write(config)

        start = time.time()
            #print os.path.join('..',path)
        res = subprocess.call(["./simplemd", os.path.join('..',path)])
        dt = time.time() - start if res == 0 else 'NA'
        times.append((params, dt))


    write_times(times, path = '{0}_times.csv'.format('_'.join(constrained_random_config.keys())))
