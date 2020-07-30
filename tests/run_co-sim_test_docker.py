#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.orchestrator.run_exploration import run_exploration_2D
import mpi4py.MPI as MPI
from example.parameter import test_nest as parameter_test

# File for testing the co-simulation with a docker image

def run_exploration(path,begin,end):
    parameter_test.path = "/home/example/parameter/data_mouse/"
    parameter_test.param_co_simulation['co-simulation']=True
    parameter_test.param_co_simulation['nb_MPI_nest']=MPI.COMM_WORLD.Get_size()
    parameter_test.param_nest['total_num_virtual_procs']=10
    parameter_test.param_co_simulation['id_region_nest']=[1,2]
    parameter_test.param_co_simulation['synchronization']=11.0
    run_exploration_2D(path, parameter_test, {'g':[1.0], 'mean_I_ext': [0.0]}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==4:
        run_exploration(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))
    elif len(sys.argv)==1:
        run_exploration( './test_nest/test_file/', 0.0, 10000.0)
    else:
        print('missing argument')