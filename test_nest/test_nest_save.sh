#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test the saving histogram with MPI

# configuration variable
. ./init.sh

DELAY=100.0

mkdir ./test_nest_to_save
mkdir ./test_nest_to_save/input/
mkdir ./test_nest_to_save/save/
mkdir ./test_nest_to_save/log/

DELAY=100.0

# shellcheck disable=SC2089
parameter='param_record_MPI = {"save_step": 10, "resolution": 0.1, "synch": '"${DELAY}"', "level_log": 0}'
echo "${parameter}" >./test_nest_to_save/parameter.py

$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/nest_save_hist.py ../test_nest/test_nest_to_save/ input/0.txt ../test_nest/test_nest_to_save/save/test 10000 &
sleep 10 # wait for creation of file
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_input_nest_to_tvb.py  ../test_nest/test_nest_to_save/input/0.txt $DELAY &

wait

rm  -rd test_nest_to_save
