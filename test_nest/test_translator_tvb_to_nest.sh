#!/bin/bash
DELAY=100.0
mkdir ./test_tvb_to_nest
mkdir ./test_tvb_to_nest/input/
mkdir ./test_tvb_to_nest/output/
mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/tvb_to_nest.py ../test_nest/test_tvb_to_nest/output/ 0 10 ../input/0.txt 0.5 &
PID_1=$(echo $!)
sleep 10 # wait for creatiion of file
mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/test_file/test_input_tvb_to_nest.py  ../test_nest/test_tvb_to_nest/input/0.txt $DELAY &
PID_2=$(echo $!)
mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/test_file/test_receive_tvb_to_nest.py  ../test_nest/test_tvb_to_nest/output/0.txt &
PID_3=$(echo $!)

wait $PID_1
rm  -rd test_tvb_to_nest
