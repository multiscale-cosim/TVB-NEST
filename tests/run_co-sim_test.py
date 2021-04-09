#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Universit_spikeé
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.launcher.run_exploration import run_exploration_2D
from example.parameter import test_nest as parameter_test

# file for testing the co-simulation

def run_exploration(path,begin,end,nb_VP,nb_mpi,cluster):
    parameter_test.param_co_simulation['co-simulation']=True
    parameter_test.param_co_simulation['translation_thread'] = 2
    parameter_test.param_co_simulation['nb_MPI_nest']=nb_mpi
    parameter_test.param_nest['total_num_virtual_procs']=nb_VP
    parameter_test.param_nest_topology['nb_neuron_by_region'] = 1000
    parameter_test.param_co_simulation['id_region_nest']=[1,2]
    parameter_test.param_co_simulation['synchronization']=3.5
    parameter_test.param_nest_background['multimeter']=False
    parameter_test.param_nest_background['record_spike']=False
    parameter_test.param_nest_topology['sigma_V_0'] = 200.0
    run_exploration_2D(path, parameter_test, {'g':[1.0], 'mean_I_ext': [100.0]}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==5:
        run_exploration( sys.argv[1], 0.0, 210.0, int(sys.argv[2]),int(sys.argv[3]),sys.argv[4].lower() == 'true')
    else:
        print('missing argument')
