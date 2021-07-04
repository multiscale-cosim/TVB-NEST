#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../lib/lib_py/lib/python3.8/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest/lib/python3.8/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=${PWD}/../lib/lib_py/bin:$PATH


#for i in {10,13,16,20,26,33,42,53,67,85,108,137,174,221,281,356,452,574,728,924,1172,1487,1887,2395,3039,3857,4894,6210,7880,10000}
for i in {10,14,19,26,36,49,67,92,127,174,240,329,452,621,853,1172,1610,2212,3039,4175,5736,7880,10826,14874,20434,28072,38566,52983,72790,100000}
do
  python3 ./run_co-sim_neuron.py './test_file/neuron/' 0.0 1000.0 $i
done