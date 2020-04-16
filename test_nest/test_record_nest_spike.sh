#!/bin/bash

PACKAGE=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/
PYTHONLIB=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages
REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/nest-run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/3.txt &
PID_1=$(echo $!)
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/4.txt &
PID_2=$(echo $!)

mpirun -n 1 python3 ../nest-io/pynest/examples/spikedetector_mpi.py

rm  4.txt
rm  3.txt
kill $PID_1
kill $PID_2
