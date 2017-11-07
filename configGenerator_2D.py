#!/usr/bin/python

import os
import numpy as np

BASE_DIR = os.getcwd()      # if we get amibitous, this could become a command line param
output_folder = 'configs'   # this too

# these are defautls which are used if certain parameters aren't defined for generateConfig_2D
default_params = {'TEMP':2.5, 'V_x':1, 'V_y':1.5, 'DELTA_T':0.002, 'TIMESTEPS':1000, 'BLOCK_SIZE':100,
                  'CUTOFF_RADIUS':2.5, 'LINKED_CELL_SIZE_X':2.5, 'LINKED_CELL_SIZE_Y':2.5} 

def generateConfig_2D(params):
    with open('config2D_template.xml') as f:
        template = f.read()
    for param, val in default_params.items():
        if param in params.keys():
            val = params[param]
        template = template.replace(param, str(val))
    return template

if __name__ == '__main__':
    cutoff_radius_range = np.linspace(0,5,100)
    path = os.path.join(BASE_DIR, output_folder)
    if not os.path.exists(path): os.mkdir(path)

    for cutoff_radius in cutoff_radius_range:
        params = {'CUTOFF_RADIUS':cutoff_radius}
        config = generateConfig_2D(params)
        
        filename = reduce(lambda s, param: '{0}_{1}={2:0.4f}'.format(s, param, params[param]), 
                          params, 'config2D') + '.xml'
        path = os.path.join(BASE_DIR, output_folder, filename)

        with open(path, 'w+') as f:
            f.write(config)

