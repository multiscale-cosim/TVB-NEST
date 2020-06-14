#!/usr/bin/bash

cd ../../
git submodule init
REPERTORY=$(pwd)
export PATH_INSTALATION=$REPERTORY/software/
export PATH_BUILD=$REPERTORY/build/
export PATH_GCC=$PATH_INSTALATION/gcc/
export PATH_MPI=$PATH_INSTALATION/mpi/
export PATH_CMAKE=$PATH_INSTALATION/cmake/
export PATH_PYTHON=$PATH_INSTALATION/python/
export PATH_NEST=$PATH_INSTALATION/nest
export NAME_SOURCE_NEST=$REPERTORY/nest-io-dev

export PATH=$PATH_GCC/bin/:$PATH_MPI/bin/:$PATH_CMAKE/bin/:$PATH_PYTHON/bin/:$PATH
export LD_LIBRARY_PATH=$PATH_GCC/lib/:$PATH_GCC/lib64/:$PATH_CMAKE/lib/:$PATH_MPI/lib/:$PATH_PYTHON/lib/:$LD_LIBRARY_PATH
export PYTHON_LIBRARIES=$PATH_PYTHON/lib/libpython3.7m.a
export PYTHON_INCLUDE_DIRS=$PATH_PYTHON/include/python3.7m/

mkdir $PATH_BUILD
cd $PATH_BUILD

# install gcc
mkdir gcc_install
cd gcc_install
wget http://www.netgull.com/gcc/releases/gcc-9.3.0/gcc-9.3.0.tar.gz
tar zxvf gcc-9.3.0.tar.gz 
cd gcc-9.3.0
./contrib/download_prerequisites
cd ..
mkdir objdir_gcc
cd objdir_gcc
../gcc-9.3.0/configure --prefix=$PATH_GCC --disable-multilib 
make 
make install
cd ../..

# install MPI 
mkdir mpi_install
cd mpi_install
wget -q http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz
tar xf mpich-3.1.4.tar.gz
mkdir objdir_mpi
cd objdir_mpi
../mpich-3.1.4/configure --disable-fortran --enable-fast=all,O3 --prefix=$PATH_MPI
make
make install
cd ../..

# installl CMAKE good version
mkdir cmake_install
cd cmake_install
wget https://github.com/Kitware/CMake/releases/download/v3.18.0-rc1/cmake-3.18.0-rc1.tar.gz
tar -xf cmake-3.18.0-rc1.tar.gz
mkdir objdir_cmake
cd objdir_cmake
../cmake-3.18.0-rc1/configure --prefix=$PATH_CMAKE
make 
make install
cd ../..

# installation python 
mkdir python_install
cd python_install
git clone --branch 3.7 https://github.com/python/cpython.git
mkdir objdir_python
cd objdir_python
../cpython/configure --prefix=$PATH_PYTHON CXX="$PATH_GCC/bin/g++"  CC="gcc -pthread -fPIC" --enable-optimizations
make
make install
cd ../..

cd $PATH_INSTALATION
../install/py_venv/create_virtual_python.sh
source ./tvb_nest_lib/bin/activate
cd $PATH_BUILD

## Compile and Install Nest
mkdir nest_install
cd nest_install
cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_NEST $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-readline=On -Dwith-ltdl=ON -Dwith-python=3 -Dcythonize-pynest=ON -DPYTHON_EXECUTABLE:FILEPATH=$PATH_INSTALATION/tvb_nest_lib/bin/python3.7 -DPYTHON_LIBRARY=$PATH_PYTHON/lib/libpython3.7m.so  -DPYTHON_INCLUDE_DIR=$PATH_PYTHON/include/python3.7m/
make
make install
#make test

