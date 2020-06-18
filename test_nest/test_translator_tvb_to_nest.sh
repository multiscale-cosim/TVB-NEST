#!/bin/bash
set -e #Exit on error
# Test the translator TVB to Nest

# configuration variable
. ./init.sh

#/p/project/type1_1/klijn1/code/cosim/co-simulation-tvb-nest/test_nest

DELAY=100.0

SCRATCH_DIR="./test_tvb_to_nest"

mkdir ${SCRATCH_DIR}
mkdir ${SCRATCH_DIR}/input/
mkdir ${SCRATCH_DIR}/output/
mkdir ${SCRATCH_DIR}/log/

DELAY=100.0
parameter='param_TR_tvb_to_nest = {"init": "./test_tvb_to_nest/init_rates.npy", "percentage_shared": 0.5, "seed": 42, "nb_synapses":10,"level_log": 0}'
echo "${parameter}" > ${SCRATCH_DIR}/parameter.py
cp ./init_rates.npy  ${SCRATCH_DIR}/init_rates.npy



$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/tvb_to_nest.py ${SCRATCH_DIR}/output/ 0 10 ../input/0.txt&

$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_input_tvb_to_nest.py  ${SCRATCH_DIR}/output/0_receive.txt $DELAY &
$RUN -n 1 python3 ../nest_elephant_tvb/simulation/file_translation/test_file/test_receive_tvb_to_nest.py  ${SCRATCH_DIR}/output/0_send.txt &

# Wait for all SRUNs to complete
wait


rm  -rd ${SCRATCH_DIR}
