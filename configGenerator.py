#!/usr/bin/python

import os
import csv
import time
import numpy as np
import subprocess
import random
import collections
import constraint as csp
import pickle

if __name__ == '__main__':

    solution_lists = []


    problem = csp.Problem()
    solver = csp.BacktrackingSolver()


    problem.addVariables(["MOL_X", "MOL_Y"], range(40, 45))
    problem.addVariables(["DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"], np.arange(20,35,1))
    problem.addVariables(['LINKED_CELL_SIZE_Y', 'LINKED_CELL_SIZE_X'], [0,5,10,15,20,25])
    problem.addVariables(["BLOCK_SIZE"], list([1,10,100])) #logarithmic steps
    problem.addVariables(["CUTOFF_RADIUS"], np.arange(1.25,5,0.25))


    # checkpoint bis gewissen temperatur erreicht ist
    # fix particle, aneder nur domain groesse --> immer noch mittel gross, 2k-3k
    # fix particle, irgendein cutoff, 1k steps, vtk rausschreiben, wann sind particle zufaellig verteilt

    #problem.addConstraint(lambda x, y, a, b: ((x * y) / (a * b)) < 2,
    #                      ("MOL_X", "MOL_Y", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))

    problem.addConstraint(lambda block, x, y: (x % block == 0) and (y % block == 0),
                          ("BLOCK_SIZE", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))  # you sure about this one? yes!

    problem.addConstraint(lambda cutoff, linked_x, linked_y: 2 * cutoff < min(linked_x, linked_y),
                          ("CUTOFF_RADIUS", "LINKED_CELL_SIZE_X", "LINKED_CELL_SIZE_Y"))

    print 'looking for solution'


    all_configs = problem.getSolutions()

    n=2000
    name ="full_config_lists_full.XXX"

    samples=random.sample(all_configs,2000)

    print 'pickeling'
    pickle.dump(samples, open(name, "wb"))
    print 'done'
