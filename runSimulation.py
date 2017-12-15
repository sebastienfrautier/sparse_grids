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

def generateConfig_2D(params, checkpoint=None):
    # these are defautls which are used if certain parameters aren't defined for generateConfig_2D
    defaults = {'TEMP':2.5, 'V_x':1, 'V_y':1.5, 'DELTA_T':0.002, 'TIMESTEPS':1000, 'BLOCK_SIZE':100,
                      'CUTOFF_RADIUS':3, 'LINKED_CELL_SIZE_X':3, 'LINKED_CELL_SIZE_Y':3,'DOMAIN_SIZE':5,'MOL_X':2,'MOL_Y':2}
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

if __name__ == '__main__':
    path = os.path.join(BASE_DIR, output_folder)
    if not os.path.exists(path): os.mkdir(path)

    print 'get pickled config'

    full_config = pickle.load(open("mamico_v1.1/full_config_lists_full.1111", "rb"))






    n = 500

    print 'running with %s configs' % n
    times = []
    for i in range(0, n):
        print '------------------ '+ str((1.0*i)/n)


        print 'warming up'

        this_config = random.choice(full_config)

        this_config['CHECKPOINT'] = 'checkpoints/'+''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

        config, params = generateConfig_2D(this_config)

        filename = reduce(lambda s, item: ''.format(s, *item),
                          this_config.items(), 'config2D') + '.xml'
        path = os.path.join(BASE_DIR, output_folder, filename)
        with open(path, 'w+') as f: f.write(config)

        res = subprocess.call(["./simplemd", os.path.join('..', path)])


        #####

        this_config['CHECKPOINT'] = this_config['CHECKPOINT']+'_999'

        config, params = generateConfig_2D(this_config,True)

        filename = reduce(lambda s, item: ''.format(s, *item),
                          full_config[i].items(), 'config2D') + '.xml'

        path = os.path.join(BASE_DIR, output_folder, filename)
        with open(path, 'w+') as f: f.write(config)

        start = time.time()
        res = subprocess.call(["./simplemd", os.path.join('..',path)])
        dt = time.time() - start if res == 0 else 'NA'
        times.append((params, dt))

    write_times(times, path = '{0}_times.csv'.format('_'.join(full_config[i].keys())))
