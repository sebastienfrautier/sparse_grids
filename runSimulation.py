#!/usr/bin/python
import os
import csv
import time
import numpy as np
import subprocess
import collections
import random
import sys
import constraint as csp
import argparse
import pickle
import string

BASE_DIR = os.getcwd()      # if we get amibitous, this could become a command line param
output_folder = 'configs'   # this too
output_file = '16_1_2018_1500_runs.csv'

def generateConfig_2D(params, checkpoint=None):
    # these are defautls which are used if certain parameters aren't defined for generateConfig_2D
    defaults = {'TEMP':2.5, 'V_x':1, 'V_y':1.5, 'DELTA_T':0.002, 'TIMESTEPS':1000, 'BLOCK_SIZE':100,
                      'CUTOFF_RADIUS':3, 'LINKED_CELL_SIZE_X':3, 'LINKED_CELL_SIZE_Y':3, 'MOL_X':2,'MOL_Y':2}
    defaults.update(params)

    if checkpoint:
        with open('config2D_template_checkpoint.xml') as f: template = f.read()
        for param, val in defaults.items():
            template = template.replace(param, str(val))
        return template, defaults

    else:
        with open('config2D_template.xml') as f:
            template = f.read()
        for param, val in defaults.items():
            template = template.replace(param, str(val))
        return template, defaults

def write_times(times, path = 'out.csv'):
    with open(path, 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(times)

def generateParamSpace():
    problem = csp.Problem()
    solver = csp.BacktrackingSolver()
    problem.addVariables(["MOL_X", "MOL_Y"], range(15, 100, 5))
    problem.addVariables(["DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"], range(30, 75, 5))
    problem.addVariables(['LINKED_CELL_SIZE_Y', 'LINKED_CELL_SIZE_X'], np.arange(5, 15, 2.5))
    problem.addVariables(["BLOCK_SIZE"], range(1, 10))
    problem.addVariables(["CUTOFF_RADIUS"], np.arange(0.25, 5.25, 0.25))
    problem.addConstraint(lambda x, y, a, b: ((x * y) / (a * b)) < 2,
                          ("MOL_X", "MOL_Y", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))
    problem.addConstraint(lambda block, x, y: (x % block == 0) and (y % block == 0),
                          ("BLOCK_SIZE", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))  # you sure about this one? yes!
    problem.addConstraint(lambda block, x, y: 5*block < x and 5*block < y,
                          ("BLOCK_SIZE", "LINKED_CELL_SIZE_X", "LINKED_CELL_SIZE_Y")) 
    problem.addConstraint(lambda cutoff, linked_x, linked_y: 2 * cutoff < min(linked_x, linked_y),
                          ("CUTOFF_RADIUS", "LINKED_CELL_SIZE_X", "LINKED_CELL_SIZE_Y"))
    print 'generate param space'
    return  problem.getSolutions()


if __name__ == '__main__':
    path = os.path.join(BASE_DIR, output_folder)
    if not os.path.exists(path): os.mkdir(path)

    n = 1500
    #full_config = pickle.load(open("configs_2D_param_space", "rb"))
    all_configs = generateParamSpace()
    print 'sampling %s configs' % n
    full_config = random.sample(all_configs, n)

    print 'running with %s configs' % n
    times = []
    for i in range(0, n):
        print '------------------ '+ str((1.0*i)/n)
        print 'warming up'

        config = full_config[i] #config = random.choice(full_config)

        filename = reduce(lambda s, item: '{0}_{1}={2}'.format(s, *item),
                          config.items(), 'config2D') + '.xml'
        path = os.path.join(BASE_DIR, output_folder, filename)

        config['CHECKPOINT'] = 'checkpoints/'+''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        config_str, params = generateConfig_2D(config)
        with open(path, 'w+') as f: f.write(config_str)
        res = subprocess.call(["./simplemd", os.path.join('..', path)])

        config['CHECKPOINT'] = config['CHECKPOINT']+'_999'
        config_str, params = generateConfig_2D(config, True)
        with open(path, 'w+') as f: f.write(config_str)

        start = time.time()
        res = subprocess.call(["./simplemd", os.path.join('..', path)])
        dt = time.time() - start if res == 0 else 'NA'

        times.append((params, dt))

    write_times(times, path = output_file)
