#! /bin/bash

#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# python path for neuron, project and python package
export PYTHONPATH=/home/kusch/Documents/software/neuron/neuron/lib/python:/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/:/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/lib/lib-py/lib/python3.6/site-packages:/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR//lib/nest_run/lib/python3.6/site-packages/
# add path of neuron and python executable
export PATH=/home/kusch/Documents/software/neuron/neuron/x86_64/bin/:/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/lib/lib-py/bin$:$PATH

mpirun -n 2 python3 LFP.py # use for one computer : Neuron use around 8 thread by process