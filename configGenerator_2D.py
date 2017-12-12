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

BASE_DIR = os.getcwd()      # if we get amibitous, this could become a command line param
output_folder = 'configs'   # this too

def generateConfig_2D(params):
    # these are defautls which are used if certain parameters aren't defined for generateConfig_2D
    defaults = {'TEMP':2.5, 'V_x':1, 'V_y':1.5, 'DELTA_T':0.002, 'TIMESTEPS':1000, 'BLOCK_SIZE':100,
                      'CUTOFF_RADIUS':3, 'LINKED_CELL_SIZE_X':3, 'LINKED_CELL_SIZE_Y':3,'DOMAIN_SIZE':5,'MOL_X':2,'MOL_Y':2}
    defaults.update(params)

    with open('config2D_template.xml') as f: template = f.read()
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

    parser = argparse.ArgumentParser(description='Mamico Wrapper')
    parser.add_argument('-density', type=int, help='set density range', default=100)
    parser.add_argument('-molecule', type=int, help='set molecules in both directions', default=20)
    parser.add_argument('-domain', type=int, help='set domain range in both directions', default=10)
    parser.add_argument('-linked', type=int, help='linked range', default=10)
    parser.add_argument('-block', type=int, help='block range', default=10)
    parser.add_argument('-cutoff', type=int, help='cutoff range', default=5)
    parser.add_argument('-n', type=int, help='number of draws', default=100)
    args = parser.parse_args()

    problem = csp.Problem()
    problem.addVariable("density", [random.choice(range(20, args.density))])
    problem.addVariables(["MOL_X", "MOL_Y"], range(2, args.molecule))
    problem.addVariables(["DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"], range(2, args.domain))
    problem.addVariables(['LINKED_CELL_SIZE_Y', 'LINKED_CELL_SIZE_X'], np.linspace(5,20, args.linked))
    problem.addVariables(["BLOCK_SIZE"], range(2, args.block))
    problem.addVariables(["CUTOFF_RADIUS"], range(2, args.cutoff))

    problem.addConstraint(lambda density, x, y, a, b: (x * y) / (a * b) == density,
                          ("density", "MOL_X", "MOL_Y", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))

    problem.addConstraint(lambda block, x, y: x % block and y % block,
                          ("BLOCK_SIZE", "MOL_X", "MOL_Y"))   # you sure about this one?

    problem.addConstraint(lambda cutoff, linked_x, linked_y: cutoff < linked_x and cutoff < linked_x,
                          ("CUTOFF_RADIUS", "LINKED_CELL_SIZE_X", "LINKED_CELL_SIZE_Y"))


    print 'running with %s draws' % args.n

    times = []
    for i in range(0, args.n):
        random_config = problem.getSolution() # sample from parameter space
        config, params = generateConfig_2D(random_config)

        filename = reduce(lambda s, item: '{0}_{1}={2:0.4f}'.format(s, *item),
                              random_config.items(), 'config2D') + '.xml'
        path = os.path.join(BASE_DIR, output_folder, filename)
        with open(path, 'w+') as f: f.write(config)

        start = time.time()
        res = subprocess.call(["./simplemd", os.path.join('..',path)])
        dt = time.time() - start if res == 0 else 'NA'
        times.append((params, dt))
    write_times(times, path = '{0}_times.csv'.format('_'.join(random_config.keys())))
