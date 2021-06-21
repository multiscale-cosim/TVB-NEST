#!/bin/sh

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
export DIR=$1
cd $DIR || exit

# load the module for all the installation
module load GCC/9.3.0
module load ParaStationMPI/5.4.7-1
module load CMake/3.18.0
module load Python/3.8.5
module load numba/0.51.1-Python-3.8.5
module load flex/2.6.4
module load GSL/2.6
module load SciPy-Stack/2020-Python-3.8.5
module load Boost.Python/1.74.0
module load Boost/1.74.0
module load HDF5/1.10.6
module load h5py/2.10.0-Python-3.8.5
module load mpi4py/3.0.3-Python-3.8.5


set -x
export INSTALL_FOLDER=${DIR}/../../lib/
export PYTHON_FOLD=${INSTALL_FOLDER}/lib_py
export PYTHON_LIB=${PYTHON_FOLD}/lib64/python3.8/site-packages/
export NEST_PY=${INSTALL_FOLDER}/nest_run/lib64/python3.8/site-packages/
export PROJECT_LIB=${DIR}/../..
export PATH=${INSTALL_FOLDER}/lib/nest_run/bin/:$PATH

source ${PYTHON_FOLD}/bin/activate

export PYTHONPATH=${NEST_PY}:${PYTHON_LIB}:${PROJECT_LIB}:$PYTHONPATH

python3 $2/nest_elephant_tvb/launcher/run_exploration.py $3
deactivate

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
