from subprocess import call
import datetime
from os import listdir

times = []
path_to_config = "/sparse_grid/configs/"
file_names = listdir(path_to_config)

for ele in file_names:
    start_time =  datetime.datetime.now()
    call(["./simplemd", path_to_config+ele])
    end_time = datetime.datetime.now()
    times.append((ele,end_time - start_time))
    call(["./simplemd", path_to_config + ele])

print times
