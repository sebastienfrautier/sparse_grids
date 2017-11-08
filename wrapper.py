from subprocess import call,CalledProcessError
import datetime
from os import listdir

times = []
path_to_config = "/sparse_grid/configs/"
file_names = listdir(path_to_config)

for ele in file_names:
    try:
        start_time =  datetime.datetime.now()
        call(["./simplemd", path_to_config+ele])
        end_time = datetime.datetime.now()
        times.append((ele,(end_time - start_time).total_seconds()))
        call(["./simplemd", path_to_config + ele])
    except CalledProcessError as exc:
        times.append((ele, "fail"))
    else:
        times.append((ele, "else"))
