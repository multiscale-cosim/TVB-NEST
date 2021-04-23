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
module load daint-gpu
module load cray-python/3.8.5.0
module load CMake/3.14.5
module load Boost/1.70.0-CrayGNU-20.11-python3
module load GSL/2.5-CrayGNU-20.11
module load python_virtualenv/15.0.3

export CRAYPE_LINK_TYPE=dynamic
export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
export LD_PRELOAD=/opt/cray/pe/libsci/20.09.1/CRAYCLANG/9.0/x86_64/lib/libsci_cray_mp.so.5:$LD_PRELOAD

INSTALL_FOLDER=${DIR}/../../lib/
mkdir "$INSTALL_FOLDER"

# install module of python
PYTHON_LIB=${INSTALL_FOLDER}/lib_py
mkdir "$PYTHON_LIB"
export PYTHONPATH=$PYTHON_LIB/lib/python3.8/site-packages/:$PYTHONPATH
python -m venv --system-site-packages $PYTHON_LIB
source $PYTHON_LIB/bin/activate
pip install junitparser
pip install elephant
pip install requests
pip install tvb-data tvb-gdist tvb-library
rm $PYTHON_LIB/lib/python3.8/site-packages/typing.py

cd $INSTALL_FOLDER
wget https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-3.0.3.tar.gz
tar -zxf mpi4py-3.0.3.tar.gz
cd mpi4py-3.0.3

echo " # Default configuration
 ---------------------
[mpi-piz-daint]

mpi_dir              = /opt/cray/pe/mpt/7.7.16/gni/mpich-crayclang/

mpicc                = /opt/cray/pe/craype/2.7.3/bin/cc
mpicxx               = /opt/cray/pe/craype/2.7.3/bin/CC

extra_link_args   = -lmpich_gnu_82_dpm
" >> mpi.cfg
python setup.py build --mpi=mpi-piz-daint
python setup.py install
cd ..
rm -rd mpi4py-3.0.3 mpi4py-3.0.3.tar.gz

# build nest
PATH_INSTALLATION=${DIR}/../../nest-io-dev
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
         -Dwith-readline=OFF -Dwith-ltdl=ON \
         -DPYTHON_LIBRARY=/opt/python/3.8.5.0/lib/libpython3.8.so \
         -DPYTHON_INCLUDE_DIR=/opt/python/3.8.5.0/include/python3.8/
# need to this line at the line 485 of cmake/ProcessOptions.cmake for include flags
#set( MPI_CXX_COMPILE_FLAGS "-lmpich_gnu_82_dpm")
#set( MPI_CXX_LINK_FLAGS "-lmpich_gnu_82_dpm")
make -j 8
make install

deactivate

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit