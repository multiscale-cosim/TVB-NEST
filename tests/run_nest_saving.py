#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.simulation.run_exploration import run_exploration_2D
import numpy as np
from nest_elephant_tvb.parameter import test_nest as parameter_test

# File for testing the saving of the histogram of Nest simulation

def run_exploration(path,begin,end):
    parameter_test.param_co_simulation['co-simulation']=False
    parameter_test.param_co_simulation['nb_MPI_nest']=1
    parameter_test.param_nest['total_num_virtual_procs']=10
    parameter_test.param_co_simulation['id_region_nest']=[0,1,2]
    parameter_test.param_co_simulation['synchronization']=20.0
    parameter_test.param_record_MPI['save_step']=10
    parameter_test.param_co_simulation['level_log']=1
    parameter_test.param_co_simulation['record_MPI']=True
    run_exploration_2D(path, parameter_test, {'g':np.arange(0.0, 1.0, 0.5), 'mean_I_ext': np.arange(0.0, 100.0, 50.0)}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==4:
        run_exploration(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))
    elif len(sys.argv)==1:
        run_exploration( './test_file/', 0.0, 2000.0)
    else:
        print('missing argument')