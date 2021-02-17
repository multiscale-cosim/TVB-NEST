#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# Test the translator Nest to TVB

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

# configuration variable
. ./init.sh

DELAY=100.0

rm  -rd test_nest_to_tvb


mkdir ./test_nest_to_tvb
mkdir ./test_nest_to_tvb/input/
mkdir ./test_nest_to_tvb/output/
mkdir ./test_nest_to_tvb/log/

DELAY=100.0
parameter='{"param_TR_nest_to_tvb" : {"init": "./test_nest_to_tvb/init_spikes.npy", "resolution": 0.1, "synch": '${DELAY}', "width": 20.0, "nb_neurons":20, "level_log": 0}}'
echo "${parameter}" >./test_nest_to_tvb/parameter.json
cp ./init_spikes.npy  ./test_nest_to_tvb/init_spikes.npy

$RUN -n 2 python3 ../nest_elephant_tvb/translation/nest_to_tvb.py ./test_nest_to_tvb/ input/0.txt output/0.txt&
$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/test_input_nest_to_tvb.py  ./test_nest_to_tvb/input/0.txt $DELAY &
$RUN -n 1 python3 ../nest_elephant_tvb/translation/test_file/test_receive_nest_to_tvb.py  ./test_nest_to_tvb/output/0.txt &

wait
rm  -rd test_nest_to_tvb

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
