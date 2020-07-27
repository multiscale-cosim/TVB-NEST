#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test record with MPI

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

# configuration variable
. ./init.sh

mkdir test_nest_record
sleep 1

$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/record_nest_activity/record_region_activity.py  ./test_nest_record/3.txt &
$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/record_nest_activity/record_region_activity.py  ./test_nest_record/4.txt &

$RUN -n 1 python3 ./test_nest_file/spikedetector_mpi.py

rm -rd test_nest_record

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
