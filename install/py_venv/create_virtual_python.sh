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
set -x

PATH_LIB=$(pwd)
pip3.8 install virtualenv
virtualenv -p python3.8 --system-site-packages lib_py
source $PATH_LIB/lib_py/bin/activate

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

# install TVB
pip install tvb-data==2.0 tvb-gdist==2.1.0 tvb-library==2.0.10

# for LFPY
## install parameters
git clone https://github.com/NeuralEnsemble/parameters
cd parameters
git checkout b95bac2bd17f03ce600541e435e270a1e1c5a478
python3.8 setup.py install
cd ..
rm -rfd parameters
## install neurons
git clone https://github.com/neuronsimulator/nrn.git
cd nrn
git checkout 8.0.0
mkdir build
cd build
cmake .. \
-DNRN_ENABLE_INTERVIEWS=OFF \
-DNRN_ENABLE_MPI=OFF \
-DNRN_ENABLE_RX2D=OFF \
-DCMAKE_INSTALL_PREFIX=$PATH_LIB/soft
cmake --build . --parallel 7 --target install
cd ../..
rm -rfd nrn
export PYTHONPATH=$PATH_LIB/soft/lib/python/:$PYTHONPATH
## install LFPy
pip install lfpykit==0.3
pip install MEAutility==1.4.9
pip install LFPy==2.2.1
# install HybridLFPy from github
git clone --branch nest-3-lio https://github.com/lionelkusch/hybridLFPy.git
cd hybridLFPy
python3.8 setup.py install --prefix $PATH_LIB/lib_py/

cd ..
rm -rfd hybridLFPy



mkdir nest
mkdir nest_build
cd "nest_build" || exit
cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_LIB/nest $PATH_LIB/../nest-io-dev \
      -Dwith-mpi=ON \
      -Dwith-openmp=ON \
      -Dwith-readline=On \
      -Dwith-ltdl=ON \
      -Dwith-python=ON \
      -Dcythonize-pynest=ON
make
make install
cd ..
rm -rd nest_build

echo "export PYTHONPATH=$PATH_LIB/soft/lib/python/:$PATH_LIB/nest/lib/python3.8/site-packages/:$PYTHONPATH" >> $PATH_LIB/lib_py/bin/activate
echo "export PATH=$PATH_LIB/soft/bin/:$PATH_LIB/nest/bin:$PATH" >> $PATH_LIB/lib_py/bin/activate
echo "export LD_LIBRARY_PATH=$PATH_LIB/soft/lib:$LD_LIBRARY_PATH" >> $PATH_LIB/lib_py/bin/activate
deactivate
