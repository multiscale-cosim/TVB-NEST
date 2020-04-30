#!/bin/bash

# Test the translator Nest to TVB

# configuration variable
PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../venv/lib/python3.6/site-packages # folder with my virtual python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest_run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

DELAY=100.0

mkdir ./test_nest_to_tvb
mkdir ./test_nest_to_tvb/input/
mkdir ./test_nest_to_tvb/output/
mkdir ./test_nest_to_tvb/log/

parameter='param_TR_nest_to_tvb = {"init": "./test_nest_to_tvb/init_spikes.npy", "resolution": 0.1, "synch": '${DELAY}', "width": 20.0, "level_log": 0}'
echo "${parameter}" >./test_nest_to_tvb/parameter.py
cp ./init_spikes.npy  ./test_nest_to_tvb/init_spikes.npy

mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/nest_to_tvb.py ../test_nest/test_nest_to_tvb/ input/0.txt output/0.txt&
sleep 10 # wait for creation of file
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_input_nest_to_tvb.py  ../test_nest/test_nest_to_tvb/input/0.txt $DELAY &
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_receive_nest_to_tvb.py  ../test_nest/test_nest_to_tvb/output/0.txt &

wait

rm  -rd test_nest_to_tvb
