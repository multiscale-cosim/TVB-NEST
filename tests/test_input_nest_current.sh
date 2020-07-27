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

$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/input_nest_current/input_current.py ../test_nest/4.txt &
PID_1=$(echo $!)

$RUN -n 1 python3 ./test_nest_file/step_current_generator_mpi.py

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit