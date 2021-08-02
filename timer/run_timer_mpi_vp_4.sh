#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../lib/lib_py/lib/python3.8/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest/lib/python3.8/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=${PWD}/../lib/lib_py/bin:$PATH

for i in $(seq 4 4 8)
do
  for trail in {0..10}
  do
    python3 ./run_co-sim_mpi_vp_4.py './test_file/paper_mpi_vp_4/' $trail 0.0 10.0 $i
  done
done