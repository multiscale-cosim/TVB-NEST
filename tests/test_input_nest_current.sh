#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# test the input current in nest

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

# configuration variable
. ./init.sh

mkdir test_nest_current

$RUN -n 1 python3 ./test_transformation/input_nest_current/input_current.py ./test_nest_current/4.txt &
PID_1=$(echo $!)

$RUN -n 1 python3 ./test_nest_file/step_current_generator_mpi.py

rm -rd test_nest_current

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit