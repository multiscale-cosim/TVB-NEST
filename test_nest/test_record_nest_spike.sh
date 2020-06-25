#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test record with MPI

# configuration variable
. ./init.sh

$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/3.txt &
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/4.txt &

$RUN -n 1 python3 ../nest-io/pynest/examples/spikedetector_mpi.py

