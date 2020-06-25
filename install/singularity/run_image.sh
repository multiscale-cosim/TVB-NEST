#!/bin/bash

IMAGE=./install/singularity/Nest_TVB_full.simg
#IMAGE=./install/singularity/Nest_TVB.simg
#IMAGE=./install/singularity/Nest_TVB_2.simg

cd ../../
singularity run --app mpi $IMAGE -n 8 python3 test_nest/run_co-sim_test.py $(pwd)/test_nest/test_sing/ 8
cd install/singularity
