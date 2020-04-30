#!/bin/bash

# Test a simple simulation of co-simulation for different number of MPI and thread

# configuration variable
PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../venv/lib/python3.6/site-packages # folder with my virtual python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest_run/lib/python3.6/site-packages/
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