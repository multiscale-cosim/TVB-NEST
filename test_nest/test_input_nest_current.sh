#!/bin/bash

. ./init.sh

$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current.py ../test_nest/4.txt &
PID_1=$(echo $!)

$RUN -n 1 python3 ../nest-io/pynest/examples/step_current_generator_mpi.py
