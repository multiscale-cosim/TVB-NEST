#!/bin/bash

PACKAGE=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/
PYTHONLIB=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages
REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/nest-run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/spike_nest_input/input_region_activity.py  ../test_nest/7.txt &
PID_1=$(echo $!)
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/3.txt &
PID_2=$(echo $!)
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/4.txt &
PID_3=$(echo $!)

mpirun -n 1 python3 ../nest-io/pynest/examples/spikegenerator_mpi.py

rm  4.txt
rm  3.txt
kill $PID_2
kill $PID_3
