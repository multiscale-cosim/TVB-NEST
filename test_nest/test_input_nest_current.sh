#!/bin/bash

# test the input current in nest

# configuration variable
PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../venv/lib/python3.6/site-packages # folder with my virtual python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest_run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current.py ../test_nest/4.txt &
PID_1=$(echo $!)

mpirun -n 1 python3 ../nest-io/pynest/examples/step_current_generator_mpi.py
