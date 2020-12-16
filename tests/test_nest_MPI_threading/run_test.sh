#! /bin/bash

#Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
#Licensed to the Apache Software Foundation (ASF) under one
#or more contributor license agreements.  See the NOTICE file
#distributed with this work for additional information
#regarding copyright ownership.  The ASF licenses this file
#to you under the Apache License, Version 2.0 (the
#"License"); you may not use this file except in compliance
#with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing,
#software distributed under the License is distributed on an
#"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#KIND, either express or implied.  See the License for the
#specific language governing permissions and limitations
#under the License.

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR || exit
# TDO add the check part of the test

PACKAGE=${PWD}/../../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../../lib/lib-py/python3.6/site-packages # folder with python library
REPERTORY_LIB_NEST=${PWD}/../../lib/nest_run/lib/python3.6/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export RUN="mpirun"

# function for lunch test
run_test() {
nb_VP=$1
nb_mpi=$2
nb_run=$3
time_sim=$4
spike_generator=$5
parrot=$6
iaf=$7
separate=$8
nb_mpi_recorder=$9
nb_mpi_generator_spike=${10}
nb_mpi_generator_current=${11}
shared_mpi_input=${12}
mix_mpi=${13}

folder="../test_file/files/nb_VP_"${nb_VP}"nb_mpi"${nb_mpi}'_D_'${spike_generator}'_P_'${parrot}'_N_'${iaf}'_R_'${nb_mpi_recorder}'_Separate_'${separate}'_GS_'${nb_mpi_generator_spike}'_GC_'${nb_mpi_generator_current}'_SH_'${shared_mpi_input}'_SM_'${mix_mpi}

if [ -d $folder ]
then
  python3 ./check_result.py ${folder} ${nb_VP} ${nb_mpi} ${nb_run} ${time_sim} ${spike_generator} ${parrot} ${iaf} ${nb_mpi_recorder} ${separate} ${nb_mpi_generator_spike} ${nb_mpi_generator_current} ${shared_mpi_input} ${mix_mpi}
else
  mkdir -p ${folder}
  mkdir ${folder}'/log/'
  mkdir ${folder}'/file_record/'
  mkdir ${folder}'/file_gen_spike/'
  mkdir ${folder}'/file_gen_current/'
  sleep 10 # wait for creation of the folder

  for i in $(seq 1 1 ${nb_mpi_recorder})
  do
  $RUN -n 1 python3 ./record_region_activity_multiple.py  ${folder}'/file_record/' ${i} ${nb_mpi}&
  done
  sleep 1
  for i in $(seq $(( ${nb_mpi_recorder} + 1)) 1 $(( ${nb_mpi_recorder} + ${nb_mpi_generator_spike})))
  do
  $RUN -n 1 python3 ./input_region_activity_multiple.py ${folder}'/file_gen_spike/' ${i} ${nb_mpi} ${nb_run} ${time_sim}&
  done
  sleep 1
  for i in $(seq $(( ${nb_mpi_recorder} + ${nb_mpi_generator_spike} + 1)) 1 $(( ${nb_mpi_recorder} + ${nb_mpi_generator_spike} +${nb_mpi_generator_current})))
  do
  $RUN -n 1 python3 ./input_current_region_activity_multiple.py  ${folder}'/file_gen_current/' ${i} ${nb_mpi} ${nb_run} ${time_sim}&
  done

  sleep 5 # wait for creation of the file for the connection
  $RUN -n $nb_mpi python3 ./nest_config.py ${folder} ${nb_VP} ${nb_mpi} ${nb_run} ${time_sim} ${spike_generator} ${parrot} ${iaf} ${nb_mpi_recorder} ${separate} ${nb_mpi_generator_spike} ${nb_mpi_generator_current} ${shared_mpi_input} ${mix_mpi}

  wait
  python3 ./check_result ${nb_VP} ${nb_mpi} ${nb_run} ${time_sim} ${spike_generator} ${parrot} ${iaf} ${nb_mpi_recorder} ${separate} ${nb_mpi_generator_spike} ${nb_mpi_generator_current} ${shared_mpi_input} ${mix_mpi}
  if [ $? -ne 0 ]
  then
    exit
  fi
  rm -rd ${folder}
fi
}

# example test
for separate in {0,1}
do
run_test 1 1 3 200.0 2 2 2 $separate 6 6 6 0 0
done

for separate in {0,1}
do
  for nb_mpi in {1,2,4,8,16}
  do
  run_test 16 $nb_mpi 3 200.0 2 2 2 $separate 6 6 6 0 0
  done
done

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
