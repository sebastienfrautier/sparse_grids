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

n_samples = 2000
pickle_name = "rick"

if __name__ == '__main__':

    solution_lists = []
    problem = csp.Problem()
    solver = csp.BacktrackingSolver()

    problem.addVariables(["MOL_X", "MOL_Y"], range(15, 65))
    problem.addVariables(["DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"], [50])
    problem.addVariables(['LINKED_CELL_SIZE_Y', 'LINKED_CELL_SIZE_X'], [10])
    problem.addVariables(["BLOCK_SIZE"], [5])
    problem.addVariables(["CUTOFF_RADIUS"], np.arange(1.25, 5, 0.1))

    # checkpoint bis gewissen temperatur erreicht ist
    # fix particle, aneder nur domain groesse --> immer noch mittel gross, 2k-3k
    # fix particle, irgendein cutoff, 1k steps, vtk rausschreiben, wann sind particle zufaellig verteilt

    problem.addConstraint(lambda x, y, a, b: ((x * y) / (a * b)) < 2,
                          ("MOL_X", "MOL_Y", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))

    problem.addConstraint(lambda block, x, y: (x % block == 0) and (y % block == 0),
                          ("BLOCK_SIZE", "DOMAIN_SIZE_X", "DOMAIN_SIZE_Y"))  # you sure about this one? yes!

    problem.addConstraint(lambda cutoff, linked_x, linked_y: 2 * cutoff < min(linked_x, linked_y),
                          ("CUTOFF_RADIUS", "LINKED_CELL_SIZE_X", "LINKED_CELL_SIZE_Y"))

    print 'looking for solution'
    all_configs = problem.getSolutions()
    samples = random.sample(all_configs, n_samples)

    print 'pickeling'
    pickle.dump(samples, open(pickle_name, "wb"))
    print 'done'
