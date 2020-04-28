#!/bin/bash
DELAY=100.0

PACKAGE=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/
PYTHONLIB=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages
REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/nest-run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

mkdir ./test_tvb_to_nest
mkdir ./test_tvb_to_nest/input/
mkdir ./test_tvb_to_nest/output/
mkdir ./test_tvb_to_nest/log/

parameter='param_TR_tvb_to_nest = {"init": "./test_tvb_to_nest/init_rates.npy", "percentage_shared": 0.5, "seed": 42, "level_log": 0}'
echo "${parameter}" >./test_tvb_to_nest/parameter.py
cp ./init_rates.npy  ./test_tvb_to_nest/init_rates.npy

mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/tvb_to_nest.py ../test_nest/test_tvb_to_nest/output/ 0 10 ../input/0.txt&
sleep 10 # wait for creation of file
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_input_tvb_to_nest.py  ../test_nest/test_tvb_to_nest/input/0.txt $DELAY &
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_receive_tvb_to_nest.py  ../test_nest/test_tvb_to_nest/output/0.txt &

wait
rm  -rd test_tvb_to_nest
