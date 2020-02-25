#!/bin/bash

mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current.py ../test_nest/4.txt &

mpirun -n 1 python ../nest-io/pynest/examples/step_current_generator_mpi.py

rm  4.txt