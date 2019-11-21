from nest_elephant_tvb.simulation.run_exploration import run_exploration_2D
import numpy as np
from nest_elephant_tvb.parameter import test_nest as parameter_test

def run_exploration(path,begin,end):
    parameter_test.param_co_simulation['nb_MPI_nest']=0
    parameter_test.param_co_simulation['nb_MPI_tvb']=1
    parameter_test.param_topology['nb_region']=2
    parameter_test.param_tvb['Raw']=True
    run_exploration_2D(path, parameter_test, {'g':[5.0], 'mean_I_ext': [0.0]}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==4:
        run_exploration(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))
    elif len(sys.argv)==1:
        run_exploration( './test_file/two/', 0.0, 10000.0)
    else:
        print('missing argument')