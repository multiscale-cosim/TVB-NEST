#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# test the input current in nest

# configuration variable
. ./init.sh

$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/input_nest_current/input_current.py ../test_nest/4.txt &
PID_1=$(echo $!)

$RUN -n 1 python3 ../nest-io/pynest/examples/step_current_generator_mpi.py
