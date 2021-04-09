#!/bin/bash

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

# load the module for all the installation
module load daint-gpu
module load cray-python/3.8.5.0

module load CMake/3.14.5
module load GSL/2.5-CrayCCE-20.11
module load python_virtualenv/15.0.3

export DIR=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/install/piz-daint
export INSTALL_FOLDER=${DIR}/../../lib/
export PYTHON_FOLD=${INSTALL_FOLDER}/lib_py
export PYTHON_LIB=${PYTHON_FOLD}/lib_py/lib64/python3.8/site-packages/
export NEST_PY=${INSTALL_FOLDER}/nest_run/lib64/python3.8/site-packages/
export PROJECT_LIB=${DIR}/../..
export PATH=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/lib/nest_run/bin/:$PATH
export LD_PRELOAD=/opt/cray/pe/libsci/20.09.1/CRAYCLANG/9.0/x86_64/lib/libsci_cray_mp.so.5:$LD_PRELOAD

source ${PYTHON_FOLD}/bin/activate

export PYTHONPATH=${NEST_PY}:${PYTHON_LIB}:${PROJECT_LIB}:$PYTHONPATH

python $DIR/../../nest_elephant_tvb/launcher/run.py $1
desactivate

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit

