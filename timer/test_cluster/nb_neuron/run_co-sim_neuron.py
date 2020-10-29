#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.orchestrator.run_exploration import run_exploration_2D
import mpi4py.MPI as MPI
import numpy as np
from example.parameter import parameter_1 as parameter_test

# run one exploration of co-simulation for different value of the ratio between excitatory and inhibitory weight

def run_exploration(path,begin,end,nb_neurons):
    parameter_test.param_co_simulation['cluster']=True
    parameter_test.param_co_simulation['cluster_param']=' --partition=dp-eps '
    parameter_test.param_co_simulation['co-simulation']=True
    parameter_test.param_co_simulation['synchronization']=3.5
    parameter_test.param_nest_topology['nb_neuron_by_region'] = nb_neurons
    parameter_test.param_co_simulation['nb_MPI_nest']=4
    parameter_test.param_nest['total_num_virtual_procs']=4
    parameter_test.param_nest_background['multimeter'] =False
    parameter_test.param_nest_background['record_spike'] =False
    parameter_test.param_nest_connection['weight_local'] = 1.0
    run_exploration_2D(path+'/delay_vp/'+str(nb_neurons)+'/', parameter_test, {'g':np.arange(1.0, 1.2, 0.5), 'mean_I_ext': [0.0]}, begin, end)

if __name__ == "__main__":
    import sys
    import nest
    print(nest.__file__)
    if len(sys.argv)==5:
        run_exploration(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4]))
    elif len(sys.argv)==1:
        run_exploration( './test_file/time_syn/10000/', 0.0, 1000.0,1)
    else:
        print('missing argument')
