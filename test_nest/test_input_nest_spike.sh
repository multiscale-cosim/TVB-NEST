#!/bin/bash

# Expand variables and print line to be executed
set -o xtrace

# Test the input of nest

# configuration variable
. ./init.sh 

$RUN -n 1  python3 ../nest_elephant_tvb/simulation/file_translation/test_file/spike_nest_input/input_region_activity.py  ../test_nest/7.txt &
$RUN -n 1  python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/3.txt &
$RUN -n 1  python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/4.txt &

$RUN -n 1  python3 ../nest-io/pynest/examples/spikegenerator_mpi.py
