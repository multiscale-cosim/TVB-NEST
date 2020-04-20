#!/bin/bash

PACKAGE=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/
PYTHONLIB=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages
#REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/nest-run/lib/python3.6/site-packages/
REPERTORY_LIB_NEST=/home/kusch/Documents/project/co_simulation/nest/nest_run/lib/python3.6/site-packages/
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST

# test 1 : full mpi
echo "###################################### FULL MPI #################################################"
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current_multiple.py ../test_nest/4.txt 4 &
mpirun -n 4 python3 ../nest-io/pynest/examples/step_current_generator_mpi_thread.py

# test 2 : hybrid mpi and thread
echo "###################################### Hybrid #################################################"
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current_multiple.py ../test_nest/4.txt 2 &
mpirun -n 2 python3 ../nest-io/pynest/examples/step_current_generator_mpi_thread.py

# test 3 : hybrid mpi and thread
echo "###################################### thread #################################################"
mpirun -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current_multiple.py ../test_nest/4.txt 1 &
mpirun -n 1 python3 ../nest-io/pynest/examples/step_current_generator_mpi_thread.py
