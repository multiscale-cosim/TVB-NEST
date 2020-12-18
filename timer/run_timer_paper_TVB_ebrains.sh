#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../lib/lib-py/python3.6/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest_run/lib/python3.6/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=$PATH:${PWD}/../../../co_simulation/co-simulation-tvb-nest/venv/

# for bad config
for nb_neuron in {10,13,16,20,26,33,42,53,67,85,108,137,174,221,281,356,452,574,728,924,1172,1487,1887,2395,3039,3857,4894,6210,7880,10000}
do
  for trail in {0..10}
  do
      python3 ./run_co-sim_TVB_ebrains.py './test_file/benchmark_paper_ebrains/' $trail 0.0 1000.0 1 1 $nb_neuron 0.1
  done
done

# speed time_synch
for nb_neuron in {10,13,16,20,26,33,42,53,67,85,108,137,174,221,281,356,452,574,728,924,1172,1487,1887,2395,3039,3857,4894,6210,7880,10000}
do
  for trail in {0..10}
  do
      python3 ./run_co-sim_TVB_ebrains.py './test_file/benchmark_paper_ebrains/' $trail 0.0 1000.0 1 1 $nb_neuron 3.5
  done
done

# speed MPI
for nb_neuron in {10,13,16,20,26,33,42,53,67,85,108,137,174,221,281,356,452,574,728,924,1172,1487,1887,2395,3039,3857,4894,6210,7880,10000}
do
  for trail in {0..10}
  do
      python3 ./run_co-sim_TVB_ebrains.py './test_file/benchmark_paper_ebrains/' $trail 0.0 1000.0 8 8 $nb_neuron 3.5
  done
done