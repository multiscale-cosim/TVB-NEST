#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.orchestrator.run_exploration import run_exploration_2D
import numpy as np
from example.parameter import test_nest as parameter_test

# File for exploring a simulation with only tvb simulation

def run_exploration(path,begin,end):
    parameter_test.param_co_simulation['nb_MPI_nest']=0
    run_exploration_2D(path, parameter_test, {'g':np.arange(0.0, 1.0, 0.5), 'mean_I_ext': np.arange(0.0, 100.0, 50.0)}, begin, end)

if __name__ == "__main__":
    import sys
    if len(sys.argv)==4:
        run_exploration(sys.argv[1],float(sys.argv[2]),float(sys.argv[3]))
    elif len(sys.argv)==1:
        run_exploration( './test_file/tvb/', 0.0, 1000.0)
    else:
        print('missing argument')