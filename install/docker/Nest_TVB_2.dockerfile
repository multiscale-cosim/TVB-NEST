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

FROM debian:buster-slim

COPY  ./nest-io-dev /home/nest-io-dev

RUN apt-get update;\
    apt-get install -y g++ gcc gfortran make strace wget

# install MPI
RUN wget -q http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz;\
    tar xf mpich-3.1.4.tar.gz;\
    cd mpich-3.1.4;\
    ./configure --disable-fortran --enable-fast=all,O3 --prefix=/usr;\
    make -j$(nproc);\
    make install

# Install the dependance for Nest
RUN apt-get install -y build-essential cmake python3-distutils python3-dev python3.7 libltdl-dev libreadline-dev libncurses-dev libgsl-dev curl;\
    cd /root ;\
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;\
    python3.7 get-pip.py;\
    rm get-pip.py;\
    pip install --upgrade pip;\
    pip install nose;\
    pip install numpy cython Pillow;\
    pip install matplotlib;\
    pip install mpi4py;\
    apt-get install -y liblapack-dev;\
    pip install scipy ;\
    pip install elephant

# install TVB
RUN apt-get install -y llvm-dev llvm;\
    export LLVM_CONFIG=/usr/bin/llvm-config;\
    pip install tvb-data tvb-gdist tvb-library

# Compile and Install package for Nest
RUN cd /home/;\
    NAME_SOURCE_NEST=/home/nest-io-dev;\
    PATH_INSTALATION=/usr/lib/nest/;\
    PATH_BUILD=/home/nest-simulator-build;\
    export PATH_INSTALATION;\
    export PATH_BUILD	;\
    export NAME_SOURCE_NEST;\
    export NEST_DATA_PATH=$PATH_BUILD/pynest;\
    export PYTHONPATH=$PATH_INSTALATION/lib/python3.7/site-packages:$PYTHONPATH;\
    export PATH=$PATH:$PATH_INSTALATION/bin;\
    mkdir $PATH_BUILD;\
    cd $PATH_BUILD;\
    cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_INSTALATION $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-readline=On -Dwith-ltdl=ON -Dwith-python=ON -Dcythonize-pynest=ON ;\
    make;\
    make install
    #make installcheck

ENV PYTHONPATH=/usr/lib/nest/lib/python3.7/site-packages/:/home/:$PYTHONPATH

