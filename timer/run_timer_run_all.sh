#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../lib/lib_py/lib/python3.8/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest/lib/python3.8/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=${PWD}/../lib/lib_py/bin:$PATH

for i in {1..12}
do
  for trail in {0..10}
  do
    python3 ./run_co-sim_mpi.py './test_file/paper_mpi/' $trail 0.0 1000.0 $i
  done
done

for i in {1..12}
do
  for trail in {0..10}
  do
    python3 ./run_co-sim_thread.py './test_file/paper_time_thread/' $trail 0.0 1000.0 $i
  done
done

for i in $(seq 2 2 12)
do
  for trail in {0..10}
  do
    python3 ./run_co-sim_mpi_vp_2.py './test_file/paper_mpi_vp_2/' $trail 0.0 1000.0 $i
  done
done

for i in $(seq 4 4 12)
do
  for trail in {0..10}
  do
    python3 ./run_co-sim_mpi_vp_4.py './test_file/paper_mpi_vp_4/' $trail 0.0 1000.0 $i
  done
done

for i in {10,14,19,26,36,49,67,92,127,174,240,329,452,621,853,1172,1610,2212,3039,4175,5736,7880,10826,14874,20434,28072,38566,52983,72790,100000}
do
  for trail in {0..10}
  do
    python3 ./run_co-sim_neuron.py './test_file/paper_nb_neurons/' $trail 0.0 1000.0 $i
  done
done

#for i in  0.1 0.2 0.4 0.5 0.8 0.9 1.0 1.1 1.3 1.5 1.6 1.7 1.8 2.0 2.1 2.2 2.5 2.6 2.7 3.0 3.1 3.2 3.4 3.5
for i in  0.1 0.2 0.4 0.5 0.8 0.9 1.0 1.1 1.3 1.5 1.6 1.7 1.8 2.0 2.1
do
  for trail in {0..10}
  do
    python3 ./run_co-sim_time.py './test_file/paper_time_synch/' $trail 0.0 1000.0 $i
  done
done

