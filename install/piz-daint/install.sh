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

set -x

export CRAYPE_LINK_TYPE=dynamic
export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
export LD_PRELOAD=/opt/cray/pe/libsci/20.09.1/CRAYCLANG/9.0/x86_64/lib/libsci_cray_mp.so.5:$LD_PRELOAD

INSTALL_FOLDER=${DIR}/../../lib/
mkdir "$INSTALL_FOLDER"
cd $INSTALL_FOLDER

# intall mpich
wget http://www.mpich.org/static/downloads/3.4.2/mpich-3.4.2.tar.gz
tar -xf mpich-3.4.2.tar.gz
cd mpich-3.4.2
./configure prefix=$INSTALL_FOLDER/soft --with-device=ch4:ofi:gni --with-file-system=lustre --with-pm=no --with-pmi=cray --enable-ugni-static
make 
make install
cd ..
rm -rd mpich-3.4.2.tar.gz mpich-3.4.2

export PATH=$INSTALL_FOLDER/soft/bin:$PATH
export LD_LIBRARY_PATH=$INSTALL_FOLDER/soft/lib/:$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
export CXX=$INSTALL_FOLDER/soft/bin/mpicxx
export CC=$INSTALL_FOLDER/soft/bin/mpicxx
export cc=$INSTALL_FOLDER/soft/bin/mpicc


# install module of python
PYTHON_LIB=${INSTALL_FOLDER}/lib_py
mkdir "$PYTHON_LIB"
export PYTHONPATH=$PYTHON_LIB/lib/python3.8/site-packages/:$PYTHONPATH
python -m venv --system-site-packages $PYTHON_LIB
source $PYTHON_LIB/bin/activate
pip install nose==1.3.7
pip install numpy==1.20.3 cython==0.29.23 Pillow==8.2.0
pip install mpi4py==3.0.3
pip install scipy==1.6.3
pip install elephant==0.10.0
pip install h5py==3.2.1

# install TVB
pip install tvb-data==2.0 tvb-gdist==2.1.0 tvb-library==2.0.10
rm $PYTHON_LIB/lib/python3.8/site-packages/typing.py

cd $INSTALL_FOLDER
wget https://bitbucket.org/mpi4py/mpi4py/downloads/mpi4py-3.0.3.tar.gz
tar -zxf mpi4py-3.0.3.tar.gz
cd mpi4py-3.0.3

echo " # Default configuration
 ---------------------
[mpi-piz-daint]

mpi_dir              = $INSTALL_FOLDER/soft/

mpicc                = $INSTALL_FOLDER/soft/bin/mpicc
mpicxx               = $INSTALL_FOLDER/soft/bin/mpicxx

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
         -DCMAKE_C_COMPILER=$INSTALL_FOLDER/soft/bin/mpicc -DCMAKE_CXX_COMPILER=$INSTALL_FOLDER/soft/bin/mpicxx\
         -Dwith-python=ON \
         -Dwith-mpi=ON -Dwith-openmp=ON \
         -Dwith-readline=OFF -Dwith-ltdl=ON \
         -DPYTHON_LIBRARY=/opt/python/3.8.5.0/lib/libpython3.8.so \
         -DPYTHON_INCLUDE_DIR=/opt/python/3.8.5.0/include/python3.8/ \
	 -DMPI_C_INCLUDE_PATH=$INSTALL_FOLDER/soft/include -DMPI_C_LIB_NAMES=C -DMPI_C_LIBRARY=$INSTALL_FOLDER/soft/lib/libmpi.so.12.1.11 \
	 -DMPI_CXX_INCLUDE_PATH=$INSTALL_FOLDER/soft/include -DMPI_CXX_LIB_NAMES=CXX -DMPI_CXX_LIBRARY=$INSTALL_FOLDER/soft/lib/libmpicxx.so.12.1.11
make
make install

deactivate

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
