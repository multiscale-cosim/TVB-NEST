#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.orchestrator.run_exploration import run_exploration_2D
import numpy as np
from timer import parameter

# exploration performance for different number o thread

def run_exploration(path,begin,end,nb_th):
    parameter.param_co_simulation['co-simulation']=True
    parameter.param_nest_topology['nb_neuron_by_region'] = 10000
    parameter.param_co_simulation['nb_MPI_nest']=1
    parameter.param_nest['total_num_virtual_procs']=nb_th
    parameter.param_nest_background['multimeter'] =False
    parameter.param_nest_background['record_spike'] =False
    parameter.param_nest_connection['weight_local'] = 1.0
    run_exploration_2D(path+'/'+str(nb_th)+'/', parameter, {'g':np.arange(1.0, 1.2, 0.5), 'mean_I_ext': [0.0]}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==5:
        run_exploration(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4]))
    elif len(sys.argv)==1:
        run_exploration( './test_file/thread/', 0.0, 1000.0,1)
    else:
        print('missing argument')