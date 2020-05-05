#!/bin/bash

# Test the translator Nest to TVB

# configuration variable
. ./init.sh

DELAY=100.0

mkdir ./test_nest_to_tvb
mkdir ./test_nest_to_tvb/input/
mkdir ./test_nest_to_tvb/output/
mkdir ./test_nest_to_tvb/log/

DELAY=100.0
parameter='param_TR_nest_to_tvb = {"init": "./test_nest_to_tvb/init_spikes.npy", "resolution": 0.1, "synch": '${DELAY}', "width": 20.0, "level_log": 0}'
echo "${parameter}" >./test_nest_to_tvb/parameter.py
cp ./init_spikes.npy  ./test_nest_to_tvb/init_spikes.npy

$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/nest_to_tvb.py ../test_nest/test_nest_to_tvb/ input/0.txt output/0.txt&
sleep 10 # wait for creation of file
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_input_nest_to_tvb.py  ../test_nest/test_nest_to_tvb/input/0.txt $DELAY &
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_receive_nest_to_tvb.py  ../test_nest/test_nest_to_tvb/output/0.txt &

wait

rm  -rd test_nest_to_tvb
