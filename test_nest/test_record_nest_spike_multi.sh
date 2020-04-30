#!/bin/bash

# Test record with MPI with different number of thread and MPI

# configuration variable
PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../venv/lib/python3.6/site-packages # folder with my virtual python library
REPERTORY_LIB_NEST=${PWD}/../lib/nest_run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

# test 1 : full mpi
echo "###################################### FULL MPI #################################################"
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/3.txt 4 &
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/4.txt 4 &
mpirun -n 4 python3 ../nest-io/pynest/examples/spikedetector_mpi_thread.py

# test 2 : hybrid mpi and thread
echo "###################################### Hybrid #################################################"
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/3.txt 2 &
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/4.txt 2 &
mpirun -n 2 python3 ../nest-io/pynest/examples/spikedetector_mpi_thread.py

# test 3 : hybrid mpi and thread
echo "###################################### thread #################################################"
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/3.txt 1 &
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/4.txt 1 &
mpirun -n 1 python3 ../nest-io/pynest/examples/spikedetector_mpi_thread.py
