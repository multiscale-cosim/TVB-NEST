#!/bin/bash

PACKAGE=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/
PYTHONLIB=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages
#REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/nest-run/lib/python3.6/site-packages/
REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/nest/nest_run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current.py ../test_nest/4.txt &
PID_1=$(echo $!)

mpirun -n 1 python3 ../nest-io/pynest/examples/step_current_generator_mpi.py
