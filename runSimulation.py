#!/usr/bin/python
import os
import csv
import time
import numpy as np
import subprocess
import collections
import random
import sys
import argparse
import constraint as csp
import argparse
import pickle
import string

BASE_DIR = os.getcwd()
output_folder = 'configs'

def generateConfig_2D(params, checkpoint=None):
    # these are defautls which are used if certain parameters aren't defined for generateConfig_2D
    defaults = {'TEMP':2.5, 'V_x':1, 'V_y':1.5, 'DELTA_T':0.002, 'TIMESTEPS':1000, 'BLOCK_SIZE':100,
                      'CUTOFF_RADIUS':3, 'LINKED_CELL_SIZE_X':3, 'LINKED_CELL_SIZE_Y':3, 'MOL_X':2,'MOL_Y':2}
    defaults.update(params)

    if checkpoint:
        with open('templates/config2D_template_checkpoint.xml') as f: template = f.read()
        for param, val in defaults.items():
            template = template.replace(param, str(val))
        return template, defaults

    else:
        with open('templates/config2D_template.xml') as f:
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
    problem.addVariables(["MOL_X", "MOL_Y"], range(15, 100, 5))
    problem.addVariables(["DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"], range(25, 70, 5))
    problem.addVariables(['LINKED_CELL_SIZE_Y', 'LINKED_CELL_SIZE_X'], np.arange(1.25, 7.5, 1.25))
    problem.addVariables(["BLOCK_SIZE"], [10**i for i in range(5)])
    problem.addVariables(["CUTOFF_RADIUS"], np.arange(1.2, 6.2, 0.2))

    problem.addConstraint(lambda molecules, direction: molecules <= direction, ("MOL_X","DOMAIN_SIZE_X"))
    problem.addConstraint(lambda molecules, direction: molecules <= direction, ("MOL_Y","DOMAIN_SIZE_Y")) 

    problem.addConstraint(lambda domain_size, cell_size: (domain_size % cell_size) == 0, ("DOMAIN_SIZE_X", "LINKED_CELL_SIZE_X"))
    problem.addConstraint(lambda domain_size, cell_size: (domain_size % cell_size) == 0, ("DOMAIN_SIZE_Y", "LINKED_CELL_SIZE_Y"))

    problem.addConstraint(lambda domain_size, cell_size: (domain_size / cell_size) >= 4, ("DOMAIN_SIZE_X", "LINKED_CELL_SIZE_X"))
    problem.addConstraint(lambda domain_size, cell_size: (domain_size / cell_size) >= 4, ("DOMAIN_SIZE_Y", "LINKED_CELL_SIZE_Y"))
    
    density = lambda mol_x, mol_y, domain_x, domain_y: (1.0*mol_x*mol_y)/(1.0*domain_x*domain_y)
    problem.addConstraint(lambda *args: density(*args) < 1.0, ("MOL_X", "MOL_Y", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))

    problem.addConstraint(lambda cutoff, linked_x, linked_y: cutoff <= min(linked_x, linked_y),
                          ("CUTOFF_RADIUS", "LINKED_CELL_SIZE_X", "LINKED_CELL_SIZE_Y"))
    return problem.getSolutions()

def runSimulation(n, output_file):
    path = os.path.join(BASE_DIR, output_folder)
    if not os.path.exists(path): os.mkdir(path)

    all_configs = generateParamSpace()
    full_config = random.sample(all_configs, n)

    print 'running with %s configs' % n
    times = []
    for i in range(0, n):
        print '------------------ '+ str((1.0*i)/n)
        print 'warming up'

        config = full_config[i] #config = random.choice(full_config)
        filename = reduce(lambda s, item: '{0}_{1}={2}'.format(s, *item), config.items(), 'config2D') + '.xml'
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

def clean_temp_files():
    try:
        subprocess.call(['bash',  'clean'])
    except Exception as e:
        print e

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('N', type=int, help='number of samples to take from parameter space')
    parser.add_argument('output_file', help='path to save (parameter, time) pairs')
    args = parser.parse_args()
                        
    runSimulation(args.N, args.output_file)
    clean_temp_files()
