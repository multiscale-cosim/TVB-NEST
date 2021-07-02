#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../lib/tvb_nest_lib/python3.8/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest_run/lib/python3.8/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=$PATH:${PWD}/../lib/tvb_nest_lib/bin

#for i in  0.1 0.2 0.4 0.5 0.8 0.9 1.0 1.1 1.3 1.5 1.6 1.7 1.8 2.0 2.1 2.2 2.5 2.6 2.7 3.0 3.1 3.2 3.4 3.5
for i in  0.1 0.2 0.4 0.5 0.8 0.9 1.0 1.1 1.3 1.5 1.6 1.7 1.8 2.0 2.1
do
  for trail in {0..0}
  do
    python3 ./run_co-sim_time.py './test_file/paper_time_synch/' $trail 0.0 1000.0 $i
  done
done
