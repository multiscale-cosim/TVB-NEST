#!/bin/bash

IMAGE=./install/singularity/Nest_TVB.simg
#IMAGE=./install/singularity/Nest_TVB_2.simg
cd ../../

singularity run --app mpi $IMAGE -n 2 python3 test_nest/run_co-sim_test.py
