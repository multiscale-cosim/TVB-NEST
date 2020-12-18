#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.orchestrator.run_exploration import run_exploration_2D
import numpy as np
from timer import parameter

# run one simulation for testing everything

def run_exploration(path,begin,end):
    parameter.param_co_simulation['co-simulation']=True
    parameter.param_nest_topology['nb_neuron_by_region'] = 10
    parameter.param_co_simulation['synchronization']=0.1
    parameter.param_co_simulation['MPI_nest']=1
    parameter.param_nest['total_num_virtual_procs']=1
    parameter.param_nest_background['multimeter'] =False
    parameter.param_nest_background['record_spike'] =False
    parameter.param_nest_connection['weight_local'] = 1.0
    run_exploration_2D(path, parameter, {'g':np.arange(1.0, 1.2, 0.5), 'mean_I_ext': [0.0]}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==4:
        run_exploration(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))
    elif len(sys.argv)==1:
        run_exploration( './test_file/benchmark_paper_ebrains/0.1/10/1/1/0/_g_1.0_mean_I_ext_0.0/', 0.0, 1000.0)
    else:
        print('missing argument')