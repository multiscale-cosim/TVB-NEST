#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

CLUSTER=false  #false/true
DEEPEST=false  #false/true

if [ "$CLUSTER" = true ]
then
    OPTIONS_SLURM=""
    if [ "$DEEPEST" = true ]
    then 
        module load CMake/3.14.0
        module load intel-para/2019a.1 # for MPI and compiler
        module load Intel/2019.5.281-GCC-8.3.0
        module load GSL/2.5
        module load Python/3.6.8 # already some module in side ( example : pip)
        module load SciPy-Stack/2019a-Python-3.6.8 mpi4py/3.0.1-Python-3.6.8
        OPTIONS_SLURM="--partition=dp-cn"
    fi

    PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
    PYTHONLIB=../lib/site_packages # folder with python library
    REPERTORY_LIB_NEST=../lib/nest_run/lib64/python3.6/site-packages/ # folder with py-nest
    export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
    RUN="srun "${OPTIONS_SLURM}
else
    echo " WARNING the python path are not defene"

    PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
    # PYTHONLIB=${PWD}/../venv/lib/python3.6/site-packages # folder with python library
    REPERTORY_LIB_NEST=${PWD}/../lib/nest/lib/python3.8/site-packages/ # folder with py-nest
    export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
    RUN="mpirun"
fi
    


