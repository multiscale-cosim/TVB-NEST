#!/usr/bin/bash

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
cd "$DIR" || exit

cd ../
git submodule init
REPERTORY=$(pwd)
export PATH_INSTALLATION=$REPERTORY/lib/
export PATH_BUILD=$PATH_INSTALLATION/build/
export PATH_GCC=$PATH_INSTALLATION/gcc/
export PATH_MPI=$PATH_INSTALLATION/mpi/
export PATH_CMAKE=$PATH_INSTALLATION/cmake/
export PATH_PYTHON=$PATH_INSTALLATION/python/
export PATH_NEST=$PATH_INSTALLATION/nest
export NAME_SOURCE_NEST=$REPERTORY/nest-io-dev

export PATH=$PATH_GCC/bin/:$PATH_MPI/bin/:$PATH_CMAKE/bin/:$PATH_PYTHON/bin/:$PATH
export LD_LIBRARY_PATH=$PATH_GCC/lib/:$PATH_GCC/lib64/:$PATH_CMAKE/lib/:$PATH_MPI/lib/:$PATH_PYTHON/lib/:$LD_LIBRARY_PATH
export PYTHON_LIBRARIES=$PATH_PYTHON/lib/libpython3.7m.a
export PYTHON_INCLUDE_DIRS=$PATH_PYTHON/include/python3.7m/

mkdir "$PATH_INSTALLATION"
mkdir "$PATH_BUILD"
cd "$PATH_BUILD" || exit

# install gcc
mkdir gcc_install
cd "gcc_install" || exit
wget http://www.netgull.com/gcc/releases/gcc-9.3.0/gcc-9.3.0.tar.gz
tar zxvf gcc-9.3.0.tar.gz
cd "gcc-9.3.0" || exit
./contrib/download_prerequisites
cd ..
mkdir objdir_gcc
cd "objdir_gcc" || exit
../gcc-9.3.0/configure --prefix="$PATH_GCC" --disable-multilib
make
make install
cd ../..

# install MPI
mkdir mpi_install
cd "mpi_install" || exit
wget -q http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz
tar xf mpich-3.1.4.tar.gz
mkdir objdir_mpi
cd "objdir_mpi" || exit
../mpich-3.1.4/configure --disable-fortran --enable-fast=all,O3 --prefix=$PATH_MPI
make
make install
cd ../..

# installl CMAKE good version
mkdir cmake_install
cd "cmake_install" || exit
wget https://github.com/Kitware/CMake/releases/download/v3.18.0-rc1/cmake-3.18.0-rc1.tar.gz
tar -xf cmake-3.18.0-rc1.tar.gz
mkdir objdir_cmake
cd "objdir_cmake" || exit
../cmake-3.18.0-rc1/configure --prefix="$PATH_CMAKE"
make
make install
cd ../..

# installation python 
mkdir python_install
cd "python_install" || exit
git clone --branch 3.7 https://github.com/python/cpython.git
mkdir objdir_python
cd "objdir_python" || exit
../cpython/configure --prefix="$PATH_PYTHON" CXX="$PATH_GCC/bin/g++"  CC="gcc -pthread -fPIC" --enable-optimizations
make
make install
cd ../..

cd "$PATH_INSTALLATION" || exit
../install/py_venv/create_virtual_python.sh
source ./tvb_nest_lib/bin/activate
cd "$PATH_BUILD" || exit

## Compile and Install Nest
mkdir nest_install
cd "nest_install" || exit
cmake -DCMAKE_INSTALL_PREFIX:PATH="$PATH_NEST" $NAME_SOURCE_NEST \
      -Dwith-mpi=ON \
      -Dwith-openmp=ON \
      -Dwith-readline=On \
      -Dwith-ltdl=ON \
      -Dwith-python=3 \
      -Dcythonize-pynest=ON \
      -DPYTHON_EXECUTABLE:FILEPATH="$PATH_INSTALLATION/tvb_nest_lib/bin/python3.7" \
      -DPYTHON_LIBRARY="$PATH_PYTHON/lib/libpython3.7m.so"  \
      -DPYTHON_INCLUDE_DIR="$PATH_PYTHON/include/python3.7m/"
make
make install
#make test

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
