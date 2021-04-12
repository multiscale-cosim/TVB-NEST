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

rm  -rd test_tvb_to_nest

mkdir ./test_tvb_to_nest
mkdir ./test_tvb_to_nest/nest
mkdir ./test_tvb_to_nest/translation
mkdir ./test_tvb_to_nest/translation/spike_generator
mkdir ./test_tvb_to_nest/translation/receive_from_tvb
mkdir ./test_tvb_to_nest/log/

parameter='{"param_co_simulation": {"id_region_nest":[0]},"param_TR_tvb_to_nest" : {"init": "./test_tvb_to_nest/init_rates.npy", "resolution": 0.1, "synch": '${DELAY}',"percentage_shared": 0.5, "seed": 42, "nb_synapses":10,"level_log": 0,"function_select":2, "save_spike":false, "save_rate":false}}'
echo "${parameter}" >./test_tvb_to_nest/parameter.json
cp ./init_rates.npy  ./test_tvb_to_nest/init_rates.npy

$RUN -n $1 python3 ../nest_elephant_tvb/translation/tvb_to_nest.py ./test_tvb_to_nest/ 0&
$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/test_input_tvb_to_nest.py  ./test_tvb_to_nest/translation/receive_from_tvb/0.txt $DELAY &
$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/test_receive_tvb_to_nest.py  ./test_tvb_to_nest/ translation/spike_generator/0.txt 10 &

wait
rm  -rd test_tvb_to_nest

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
