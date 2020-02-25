from nest_elephant_tvb.simulation.run_exploration import run_exploration_2D
import numpy as np
from nest_elephant_tvb.parameter import test_nest as parameter_test

def run_exploration(path,begin,end):
    parameter_test.param_co_simulation['co-simulation']=True
    parameter_test.param_co_simulation['nb_MPI_nest']=8
    parameter_test.param_nest['total_num_virtual_procs']=parameter_test.param_co_simulation['nb_MPI_nest']
    parameter_test.param_co_simulation['nb_MPI_tvb']=1
    parameter_test.param_co_simulation['id_region_nest']=[1,2]
    parameter_test.param_co_simulation['synchronization']=3.4
    run_exploration_2D(path, parameter_test, {'g':np.arange(1.0, 1.2, 0.5), 'mean_I_ext': [0.0]}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==4:
        run_exploration(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))
    elif len(sys.argv)==1:
        run_exploration( './test_file/', 0.0, 10000.0)
    else:
        print('missing argument')