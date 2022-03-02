#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test record with MPI with different number of thread and MPI

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

# configuration variable
. ./init.sh

mkdir test_nest_spike_multi
sleep 1

# test 1 : full mpi
echo "###################################### FULL MPI #################################################"
$RUN -n 1 python3 ./test_transformation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike_multi/3.txt 4 &
$RUN -n 1 python3 ./test_transformation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike_multi/4.txt 4 &
$RUN -n 4 python3 ./test_nest_file/spikedetector_mpi_thread.py

rm -rd test_nest_spike_multi
mkdir test_nest_spike_multi

# test 2 : hybrid mpi and thread
echo "###################################### Hybrid #################################################"
$RUN -n 1 python3 ./test_transformation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike_multi/3.txt 2 &
$RUN -n 1 python3 ./test_transformation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike_multi/4.txt 2 &
$RUN -n 2 python3 ./test_nest_file/spikedetector_mpi_thread.py

rm -rd test_nest_spike_multi
mkdir test_nest_spike_multi

# test 3 : hybrid mpi and thread
echo "###################################### thread #################################################"
$RUN -n 1 python3 ./test_transformation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike_multi/3.txt 1 &
$RUN -n 1 python3 ./test_transformation/record_nest_activity/record_region_activity_multiple.py  ./test_nest_spike_multi/4.txt 1 &
$RUN -n 1 python3 ./test_nest_file/spikedetector_mpi_thread.py

rm -rd test_nest_spike_multi

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
