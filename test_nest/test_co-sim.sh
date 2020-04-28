#!/bin/bash

PACKAGE=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/
PYTHONLIB=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages
REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/nest-run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

mkdir ./test_co-sim
mpirun -n 1 python3 run_co-sim_test.py ./test_co-sim/ 1
rm  -rd test_co-sim

mkdir ./test_co-sim
mpirun -n 2 python3 run_co-sim_test.py ./test_co-sim/ 2
rm  -rd test_co-sim

mkdir ./test_co-sim
mpirun -n 2 python3 run_co-sim_test.py ./test_co-sim/ 4
rm  -rd test_co-sim