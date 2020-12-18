#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.orchestrator.run_exploration import run_exploration_2D
import numpy as np
import os
from timer import parameter

# run generic exploration for performance exploration

def run_exploration(path,trial_nb,begin,end,nb_mpi,nb_thread,nb_neurons,time_synch):
    if not os.path.exists(path+'/'+str(time_synch)+'/'+str(nb_neurons)+'/'+str(nb_mpi)+'/'+str(nb_thread)+'/'+str(trial_nb)+'/'):
        parameter.param_co_simulation['co-simulation']=True
        parameter.param_co_simulation['synchronization']=time_synch
        parameter.param_nest_topology['nb_neuron_by_region'] = nb_neurons
        parameter.param_co_simulation['nb_MPI_nest']=nb_mpi
        parameter.param_nest['total_num_virtual_procs']=nb_thread
        parameter.param_nest_background['multimeter'] =False
        parameter.param_nest_background['record_spike'] =False
        parameter.param_nest_connection['weight_local'] = 1.0
        run_exploration_2D(path+'/'+str(time_synch)+'/'+str(nb_neurons)+'/'+str(nb_mpi)+'/'+str(nb_thread)+'/'+str(trial_nb)+'/', parameter, {'g':np.arange(1.0, 1.2, 0.5), 'mean_I_ext': [0.0]}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==9:
        run_exploration(sys.argv[1],int(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7]),float(sys.argv[8]))
    else:
        print('missing argument')