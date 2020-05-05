#!/bin/bash
CLUSTER=true
DEEPEST=true

if [ $CLUSTER ]
then
    if [ $DEEPEST ]
    then 
        module load CMake/3.14.0
        module load intel-para/2019a.1 # for MPI and compiler
        module load Intel/2019.5.281-GCC-8.3.0
        module load GSL/2.5
        module load Python/3.6.8 # already some module in side ( example : pip)
        module load SciPy-Stack/2019a-Python-3.6.8 mpi4py/3.0.1-Python-3.6.8
    fi

    PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
    PYTHONLIB=../lib/site_packages # folder with python library
    REPERTORY_LIB_NEST=../lib/nest_run/lib64/python3.6/site-packages/ # folder with py-nest
    export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
    RUN="srun"
else
    echo " WARNING the python path are not defene"

#    PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
#    PYTHONLIB=${PWD}/../venv/lib/python3.6/site-packages # folder with python library
#    REPERTORY_LIB_NEST=${PWD}/../lib/nest_run/lib/python3.6/site-packages/ # folder with py-nest
    export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
    RUN="mpirun"
fi
    


