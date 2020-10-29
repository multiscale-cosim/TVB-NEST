#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR || exit

CLUSTER=true  #false/true
DEEPEST=true  #false/true

if [ "$DEEPEST" = true ]
then 
    module --force purge
    module load GCCcore/.8.3.0
    module load CMake/3.14.0
    module load intel-para/2019a.1 # for MPI and compiler
    module load Intel/2019.5.281-GCC-8.3.0
    module load GSL/2.5
    module load Python/3.6.8 # already some module in side ( example : pip)
    module load SciPy-Stack/2019a-Python-3.6.8 mpi4py/3.0.1-Python-3.6.8
fi

PACKAGE=${CURRENT_REPERTORY}/../../../   # folder of co-simulation-tvb-nest
PYTHONLIB=${CURRENT_REPERTORY}/../../../lib/site_packages/ # folder with python library
REPERTORY_LIB_NEST=${CURRENT_REPERTORY}/../../../lib/nest_run/lib64/python3.6/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
