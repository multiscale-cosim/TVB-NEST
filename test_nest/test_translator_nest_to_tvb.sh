#!/bin/bash
DELAY=100.0
mkdir ./test_nest_to_tvb
mkdir ./test_nest_to_tvb/input/
mkdir ./test_nest_to_tvb/output/
mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/nest_to_tvb.py ../test_nest/test_nest_to_tvb/ input/0.txt output/0.txt 0.1 $DELAY 20 &
PID_1=$(echo $!)
sleep 10 # wait for creation of file
mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/test_file/test_input_nest_to_tvb.py  ../test_nest/test_nest_to_tvb/input/0.txt $DELAY &
PID_2=$(echo $!)
mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/test_file/test_receive_nest_to_tvb.py  ../test_nest/test_nest_to_tvb/output/0.txt &
PID_3=$(echo $!)

wait $PID_1
rm  -rd test_nest_to_tvb
