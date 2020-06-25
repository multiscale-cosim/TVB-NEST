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

module load CMake/3.14.0 
module load intel-para/2019a.1 # for MPI and compiler
module load Intel/2019.5.281-GCC-8.3.0
module load GSL/2.5
module load Python/3.6.8 # already some module in side ( example : pip)
module load SciPy-Stack/2019a-Python-3.6.8 mpi4py/3.0.1-Python-3.6.8

INSTALL_FOLDER=${PWD}/../../lib/
mkdir $INSTALL_FOLDER

# build nest
PATH_INSTALATION=${PWD}/../../nest-io-dev
PATH_BUILD=${INSTALL_FOLDER}/nest_build
PATH_RUN=${INSTALL_FOLDER}/nest_run
mkdir $PATH_BUILD
mkdir $PATH_RUN
cd ${PATH_BUILD}
cmake $PATH_INSTALATION \
	-DCMAKE_INSTALL_PREFIX:PATH=${PATH_RUN}\
	 -Dwith-python=3 -Dwith-mpi=ON \
	 -Dwith-readline=OFF \
	 -Dwith-ltdl=OFF
make -j 16 
make install

# install module of python 
PYTHON_LIB=${INSTALL_FOLDER}/site_packages
mkdir $PYTHON_LIB
export PYTHONPATH=$PYTHON_LIB:$PYTHONPATH
pip install --no-deps --target=$PYTHON_LIB numpy
pip install --no-deps --target=$PYTHON_LIB elephant neo tqdm quantities
pip install --no-deps --target=$PYTHON_LIB tvb-gdist
pip install --no-deps --target=$PYTHON_LIB tvb-data
pip install --no-deps --target=$PYTHON_LIB tvb-library llvmlite numba numexpr
