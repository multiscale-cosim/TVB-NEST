#!/bin/bash

module load CMake/3.14.0
module load intel-para/2019a.1 # for MPI and compiler
module load Intel/2019.5.281-GCC-8.3.0
module load GSL/2.5
module load Python/3.6.8 # already some module in side ( example : pip)
module load SciPy-Stack/2019a-Python-3.6.8 mpi4py/3.0.1-Python-3.6.8


PACKAGE=../../co-simulation-tvb-nest/
PYTHONLIB=../lib/site_packages
REPERTORY_LIB_NEST=../lib/nest_run/lib64/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

mkdir ./test_co-sim
mpirun -n 1 python3 run_co-sim_test.py ./test_co-sim/ 1
rm  -rd test_co-sim

mkdir ./test_co-sim
mpirun -n 2 python3 run_co-sim_test.py ./test_co-sim/ 2
rm  -rd test_co-sim

mkdir ./test_co-sim
mpirun -n 2 python3 run_co-sim_test.py ./test_co-sim/ 4
rm  -rd test_co-sim
