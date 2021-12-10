#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test a simple simulation of co-simulation for different number of MPI and thread

# configuration variable
. ./init.sh

if [ "$CLUSTER" = true ]
then
     execute=${RUN}
else
     execute=""
fi

mkdir ./test_co-sim
${execute} python3 run_co-sim_test.py ./test_co-sim/ 1 1 $CLUSTER
rm  -rd test_co-sim

# mkdir ./test_co-sim
# ${execute} python3 run_co-sim_test.py ./test_co-sim/ 4 1 $CLUSTER
# rm  -rd test_co-sim

# mkdir ./test_co-sim
# ${execute} python3 run_co-sim_test.py ./test_co-sim/ 4 2 $CLUSTER
# rm  -rd test_co-sim

# mkdir ./test_co-sim
# ${execute} python3 run_co-sim_test.py ./test_co-sim/ 4 4 $CLUSTER
# rm  -rd test_co-sim
