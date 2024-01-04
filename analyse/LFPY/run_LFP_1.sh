#! /bin/bash

#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

DIR=/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/lib/
source $DIR/lib_py/bin/activate
# python path for neuron, project and python package
export PYTHONPATH=$DIR/soft/lib/python:$DIR/..:$DIR/lib_py/lib/python3.8/site-packages:$DIR/lib_py/lib/python3.8/site-packages/hybridLFPy-0.1.4-py3.8-linux-x86_64.egg/:$DIR/nest/lib/python3.8/site-packages/:$PYTHONPATH
# add path of neuron and python executable
export PATH=$DIR/soft/bin/:$DIR/lib_py/bin:$DIR/nest/bin/:$PATH
export LD_LIBRARY_PATH=$DIR/soft/lib/:$DIR/lib_py/lib:$DIR/nest/lib

mpirun -n 1 python3 LFP.py # use for one computer : Neuron use all the core