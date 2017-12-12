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


    # setup args
    parser = argparse.ArgumentParser(description='Mamico Wrapper')

    parser.add_argument('-density', help='set density range')

    parser.add_argument('-molecule', help='set molecules in both directions')

    parser.add_argument('-domain', help='set domain range in both directions')

    parser.add_argument('-linked', help='linked range')

    parser.add_argument('-block', help='block range')

    parser.add_argument('-cutoff', help='cutoff range')

    parser.add_argument('-n', help='number of draws')

    args = parser.parse_args()


    # setup contraint problem
    problem = csp.Problem()

    problem.addVariable("density", [random.choice(range(20, int(args.density) if args.density else 100))])

    problem.addVariables(["MOL_X", "MOL_Y"], range(2, int(args.molecule) if args.molecule else 20))

    problem.addVariables(["DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"], range(2, int(args.domain) if args.domain else 20))

    problem.addVariables(['LINKED_CELL_SIZE_Y', 'LINKED_CELL_SIZE_X'], np.linspace(5,20,int(args.linked) if args.linked else 10))

    problem.addVariables(["BLOCK_SIZE"], range(2, int(args.block) if args.block else 10))

    problem.addVariables(["CUTOFF_RADIUS"], range(2, int(args.cutoff) if args.cutoff else 5))

    problem.addConstraint(lambda density, x, y, a, b: (x * y) / (a * b) == density,
                          ("density", "MOL_X", "MOL_Y", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))

    problem.addConstraint(lambda block, x, y: x % block and y % block,
                          ("BLOCK_SIZE", "MOL_X", "MOL_Y"))

    problem.addConstraint(lambda cutoff, linked_x, linked_y: cutoff < linked_x and cutoff < linked_x,
                          ("CUTOFF_RADIUS", "LINKED_CELL_SIZE_X", "LINKED_CELL_SIZE_Y"))

    # generate all solutions
    #solution = problem.getSolutions()



    # pick n random elems
    draws = int(args.n) if args.n else 100
    print 'running with %s draws' % draws

    times = []

    for i in range(0,draws):

        #constrained_random_config =random.choice(solution)
        constrained_random_config =problem.getSolution()


        config, params = generateConfig_2D(constrained_random_config)
        print config
        print params

        filename = reduce(lambda s, item: '{0}_{1}={2:0.4f}'.format(s, *item),
                              params.items(), 'config2D') + '.xml'

        path = os.path.join(BASE_DIR, output_folder, filename)
        print path
        with open(path, 'w+') as f: f.write(config)

        start = time.time()
            #print os.path.join('..',path)
        res = subprocess.call(["./simplemd", os.path.join('..',path)])
        dt = time.time() - start if res == 0 else 'NA'
        times.append((params, dt))


    write_times(times, path = '{0}_times.csv'.format('_'.join(constrained_random_config.keys())))
