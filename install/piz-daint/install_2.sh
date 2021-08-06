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
module load daint-mc
module load cray-python/3.8.5.0
module load CMake/3.14.5
module load Boost/1.70.0-CrayGNU-20.11-python3
module load GSL/2.5-CrayGNU-20.11
module load python_virtualenv/15.0.3
module load PyExtensions/python3-CrayGNU-20.11

set -x

export CRAYPE_LINK_TYPE=dynamic
export LD_LIBRARY_PATH=$CRAY_LD_LIBRARY_PATH:$LD_LIBRARY_PATH
export LD_PRELOAD=/opt/cray/pe/libsci/20.09.1/CRAYCLANG/9.0/x86_64/lib/libsci_cray_mp.so.5:$LD_PRELOAD

INSTALL_FOLDER=${DIR}/../../lib/
mkdir "$INSTALL_FOLDER"
cd $INSTALL_FOLDER

# install module of python
PYTHON_LIB=${INSTALL_FOLDER}/lib_py
mkdir "$PYTHON_LIB"
export PYTHONPATH=$PYTHON_LIB/lib/python3.8/site-packages/:$PYTHONPATH
python -m venv --system-site-packages $PYTHON_LIB
source $PYTHON_LIB/bin/activate
pip install --upgrade pip==21.1.2
pip install nose==1.3.7
pip install numpy==1.20.3 cython==0.29.23 Pillow==8.2.0
pip install mpi4py==3.0.3
pip install scipy==1.6.3
pip install elephant==0.10.0
# for plotting function
pip install matplotlib==3.4.2
pip install networkx==2.5.1
pip install h5py==3.2.1
pip install cycler==0.10.0
pip install jupyter==1.0.0
pip install vtk==9.0.1
pip install plotly==5.1.0

git clone https://github.com/NeuralEnsemble/parameters
cd parameters
git checkout b95bac2bd17f03ce600541e435e270a1e1c5a478
python3 setup.py install
cd .. 
rm -rdf parameters

git clone https://github.com/neuronsimulator/nrn.git
cd nrn
git checkout 8.0.0
mkdir build
cd build
cmake .. -DNRN_ENABLE_INTERVIEWS=OFF -DNRN_ENABLE_MPI=OFF -DNRN_ENABLE_RX3D=OFF -DNRN_ENABLE_PYTHON_DYNAMIC=ON -DPYTHON_EXECUTABLE=$(which python3.8)  -DCMAKE_INSTALL_PREFIX=$INSTALL_FOLDER/soft
make 
make install
cd ../../
rm -rdf nrn
export PYTHONPATH=$PYTHONPATH:$INSTALL_FOLDER/soft/lib/python/

pip install lfpykit==0.3
pip install MEAutility==1.4.9
pip install LFPy==2.2.1
git clone --branch nest-3-lio https://github.com/lionelkusch/hybridLFPy.git
cd hybridLFPy
python3 setup.py install
cd ..
rm -rfd hybridLFPy

# install TVB
pip install tvb-data==2.0 tvb-gdist==2.1.0 tvb-library==2.0.10
rm $PYTHON_LIB/lib/python3.8/site-packages/typing.py



## build nest
#PATH_INSTALLATION=${DIR}/../../nest-io-dev
#PATH_BUILD=${INSTALL_FOLDER}/nest_build
#PATH_RUN=${INSTALL_FOLDER}/nest_run
#
#mkdir "$PATH_BUILD"
#mkdir "$PATH_RUN"
#cd "${PATH_BUILD}" || exit
#cmake "$PATH_INSTALLATION" \
#        -DCMAKE_INSTALL_PREFIX:PATH="${PATH_RUN}"\
#         -DCMAKE_C_COMPILER=$INSTALL_FOLDER/soft/bin/mpicc -DCMAKE_CXX_COMPILER=$INSTALL_FOLDER/soft/bin/mpicxx\
#         -Dwith-python=ON \
#         -Dwith-mpi=ON -Dwith-openmp=ON \
#         -Dwith-readline=OFF -Dwith-ltdl=ON \
#         -DPYTHON_LIBRARY=/opt/python/3.8.5.0/lib/libpython3.8.so \
#         -DPYTHON_INCLUDE_DIR=/opt/python/3.8.5.0/include/python3.8/ \
#	 -DMPI_C_INCLUDE_PATH=$INSTALL_FOLDER/soft/include -DMPI_C_LIB_NAMES=C -DMPI_C_LIBRARY=$INSTALL_FOLDER/soft/lib/libmpi.so.12.1.11 \
#	 -DMPI_CXX_INCLUDE_PATH=$INSTALL_FOLDER/soft/include -DMPI_CXX_LIB_NAMES=CXX -DMPI_CXX_LIBRARY=$INSTALL_FOLDER/soft/lib/libmpicxx.so.12.1.11
#make
#make install

deactivate

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
