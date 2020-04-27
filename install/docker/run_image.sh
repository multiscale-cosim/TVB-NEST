#!/bin/bash

IMAGE=local:NEST_TVB_IO
#IMAGE=local:NEST_TVB_IO_2

cd ../../
sudo docker run -it --mount type=bind,source="$(pwd)",target=/home $IMAGE mpirun -n 2 python3 /home/test_nest/run_co-sim_test_docker.py
cd install/docker/
