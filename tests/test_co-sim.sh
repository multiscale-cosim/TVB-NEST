#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test a simple simulation of co-simulation for different number of MPI and thread

# configuration variable
. ./init.sh

mkdir ./test_co-sim
$RUN -n 1 python3 run_co-sim_test.py ./test_co-sim/ 1
rm  -rd test_co-sim

mkdir ./test_co-sim
$RUN -n 2 python3 run_co-sim_test.py ./test_co-sim/ 2
rm  -rd test_co-sim

mkdir ./test_co-sim
$RUN -n 2 python3 run_co-sim_test.py ./test_co-sim/ 4
rm  -rd test_co-sim
