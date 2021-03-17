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
module load cray-python/3.8.2.1

module load CMake/3.14.5
module load Boost/1.70.0-CrayGNU-20.08-python3
module load GSL/2.5-CrayGNU-20.08
module load python_virtualenv/15.0.3


INSTALL_FOLDER=${PWD}/../../lib/
mkdir "$INSTALL_FOLDER"

# build nest
PATH_INSTALLATION=${PWD}/../../nest-io-dev
PATH_BUILD=${INSTALL_FOLDER}/nest_build
PATH_RUN=${INSTALL_FOLDER}/nest_run
mkdir "$PATH_BUILD"
mkdir "$PATH_RUN"
cd "${PATH_BUILD}" || exit
cmake "$PATH_INSTALLATION" \
	-DCMAKE_INSTALL_PREFIX:PATH="${PATH_RUN}"\
	-DCMAKE_C_COMPILER=cc -DCMAKE_CXX_COMPILER=CC\
	 -Dwith-python=ON \
	 -Dwith-mpi=ON -Dwith-openmp=ON \
	 -Dwith-readline=ON -Dwith-ltdl=ON \
	 -Dcythonize-pynest=ON
make -j 8
make install

# install module of python 
PYTHON_LIB=${INSTALL_FOLDER}/site_packages
mkdir "$PYTHON_LIB"
export PYTHONPATH=$PYTHON_LIB:$PYTHONPATH
python -m venv $PYTHON_LIB
source $PYTHON_LIB/bin/activate
pip install elephant
pip install tvb-data tvb-gdist tvb-library
deactivate

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit

