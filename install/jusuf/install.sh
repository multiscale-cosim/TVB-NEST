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
#set -x

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
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
INSTALL_FOLDER=${DIR}/../../lib/
mkdir "$INSTALL_FOLDER"

# install module of python
PYTHON_LIB=${INSTALL_FOLDER}/lib_py
mkdir "$PYTHON_LIB"
export PYTHONPATH=$PYTHON_LIB/lib/python3.8/site-packages/:$PYTHONPATH
python -m venv --system-site-packages $PYTHON_LIB
source $PYTHON_LIB/bin/activate
pip install --no-deps --upgrade numpy
pip install junitparser
pip install elephant
pip install requests
pip install tvb-data tvb-gdist tvb-library==2.0.10
rm $PYTHON_LIB/lib/python3.8/site-packages/typing.py

# build nest
PATH_INSTALLATION=${DIR}/../../nest-io-dev
PATH_BUILD=${INSTALL_FOLDER}/nest_build
PATH_RUN=${INSTALL_FOLDER}/nest_run
mkdir "${PATH_BUILD}"
cd "${PATH_BUILD}" || exit
cmake "$PATH_INSTALLATION" \
        -DCMAKE_INSTALL_PREFIX:PATH="${PATH_RUN}"\
         -DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++\
         -Dwith-python=ON \
         -Dwith-mpi=ON -Dwith-openmp=ON \
         -Dwith-readline=OFF -Dwith-ltdl=ON
make
make install

cd $CURRENT_REPERTORY
