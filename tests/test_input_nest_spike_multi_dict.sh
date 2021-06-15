#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test the input of nest

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

# configuration variable
. ./init.sh 

mkdir test_nest_spike
sleep 1

# test 1 : full mpi
echo "###################################### FULL MPI #################################################"
$RUN -n 1 python3 ./test_translation/spike_nest_input/input_region_activity_multi.py  ./test_nest_spike/7.txt 4 &
$RUN -n 1 python3 ./test_translation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike/3.txt 4 &
$RUN -n 1 python3 ./test_translation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike/4.txt 4 &

$RUN -n 4 python3 ./test_nest_file/spikegenerator_mpi_dict.py
rm -rd test_nest_spike
mkdir test_nest_spike
sleep 1

# test 2 : hybrid mpi and thread
echo "###################################### Hybrid #################################################"
$RUN -n 1 python3 ./test_translation/spike_nest_input/input_region_activity_multi.py  ./test_nest_spike/7.txt 2 &
$RUN -n 1 python3 ./test_translation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike/3.txt 2 &
$RUN -n 1 python3 ./test_translation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike/4.txt 2 &

$RUN -n 2 python3 ./test_nest_file/spikegenerator_mpi_dict.py
rm -rd test_nest_spike
mkdir test_nest_spike
sleep 1

# test 3 : hybrid mpi and thread
echo "###################################### thread #################################################"
$RUN -n 1 python3 ./test_translation/spike_nest_input/input_region_activity_multi.py  ./test_nest_spike/7.txt 1 &
$RUN -n 1 python3 ./test_translation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike/3.txt 1 &
$RUN -n 1 python3 ./test_translation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike/4.txt 1 &

$RUN -n 1 python3 ./test_nest_file/spikegenerator_mpi_dict.py
rm -rd test_nest_spike

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit