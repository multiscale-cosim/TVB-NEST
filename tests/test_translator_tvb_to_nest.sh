#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test the translator TVB to Nest

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

# configuration variable
. ./init.sh

DELAY=100.0

mkdir ./test_tvb_to_nest
mkdir ./test_tvb_to_nest/input/
mkdir ./test_tvb_to_nest/output/
mkdir ./test_tvb_to_nest/log/

DELAY=100.0
parameter='param_TR_tvb_to_nest = {"init": "./test_tvb_to_nest/init_rates.npy", "percentage_shared": 0.5, "seed": 42, "nb_synapses":10,"level_log": 0}'
echo "${parameter}" >./test_tvb_to_nest/parameter.py
cp ./init_rates.npy  ./test_tvb_to_nest/init_rates.npy

$RUN -n 1 python3 ../nest_elephant_tvb/translation/tvb_to_nest.py ./test_tvb_to_nest/output/ 0 10 ../input/0.txt&
sleep 10 # wait for creation of file
$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/test_input_tvb_to_nest.py  ./test_tvb_to_nest/input/0.txt $DELAY &
$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/test_receive_tvb_to_nest.py  ./test_tvb_to_nest/output/0.txt &

wait
rm  -rd test_tvb_to_nest

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
