#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# test the input current in nest with different number of MPI and thread

# configuration variable
. ./init.sh

# test 1 : full mpi
echo "###################################### FULL MPI #################################################"
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current_multiple.py ../test_nest/4.txt 4 &
$RUN -n 4 python3 ../nest-io/pynest/examples/step_current_generator_mpi_thread.py

# test 2 : hybrid mpi and thread
echo "###################################### Hybrid #################################################"
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current_multiple.py ../test_nest/4.txt 2 &
$RUN -n 2 python3 ../nest-io/pynest/examples/step_current_generator_mpi_thread.py

# test 3 : hybrid mpi and thread
echo "###################################### thread #################################################"
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current_multiple.py ../test_nest/4.txt 1 &
$RUN -n 1 python3 ../nest-io/pynest/examples/step_current_generator_mpi_thread.py
