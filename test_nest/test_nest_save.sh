#!/bin/bash
DELAY=100.0

PACKAGE=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/
PYTHONLIB=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages
REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/nest-run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

mkdir ./test_nest_to_save
mkdir ./test_nest_to_save/input/
mkdir ./test_nest_to_save/save/
mkdir ./test_nest_to_save/log/

mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/nest_save_hist.py ../test_nest/test_nest_to_save/ input/0.txt ../test_nest/test_nest_to_save/save/test 0.1 $DELAY 100 13 0 &
sleep 10 # wait for creation of file
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_input_nest_to_tvb.py  ../test_nest/test_nest_to_save/input/0.txt $DELAY &

wait

rm  -rd test_nest_to_save
