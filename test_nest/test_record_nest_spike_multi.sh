#!/bin/bash

# Test record with MPI with different number of thread and MPI

# configuration variable
. ./init.sh

# test 1 : full mpi
echo "###################################### FULL MPI #################################################"
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/3.txt 4 &
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/4.txt 4 &
$RUN -n 4 python3 ../nest-io/pynest/examples/spikedetector_mpi_thread.py

# test 2 : hybrid mpi and thread
echo "###################################### Hybrid #################################################"
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/3.txt 2 &
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/4.txt 2 &
$RUN -n 2 python3 ../nest-io/pynest/examples/spikedetector_mpi_thread.py

# test 3 : hybrid mpi and thread
echo "###################################### thread #################################################"
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/3.txt 1 &
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/record_nest_activity/record_region_activity_multiple.py  ../test_nest/4.txt 1 &
$RUN -n 1 python3 ../nest-io/pynest/examples/spikedetector_mpi_thread.py
