#!/bin/bash

mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/3.txt &
mpirun -n 1 python ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity.py  ../test_nest/4.txt &

mpirun -n 1 python ../nest-io/pynest/examples/spikedetector_mpi.py

rm  4.txt
rm  3.txt
