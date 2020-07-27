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

FROM alpine:3.11

COPY ./nest-io-dev /home/nest-io-dev

RUN apk update;\
    apk add git file g++ gcc gfortran make gdb strace wget

# Install mpich
RUN wget -q http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz;\
    tar xf mpich-3.1.4.tar.gz;\
    cd mpich-3.1.4;\
    ./configure --disable-fortran --enable-fast=all,O3 --prefix=/usr;\
    make -j$(nproc);\
    make install

# Install the dependance for Nest
RUN apk add cmake readline-dev ncurses-dev gsl-dev curl python3;\
    apk add python3-dev py3-numpy-dev py3-scipy cython;\
    cd /root;\
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;\
    python3 get-pip.py;\
    rm get-pip.py;\
    pip install --upgrade pip;\
    apk add freetype-dev jpeg-dev zlib-dev;\
    pip install matplotlib;\
    pip install elephant;\
    pip install mpi4py

# install TVB
RUN apk add llvm9-dev llvm9;\
    export LLVM_CONFIG=$(which llvm-config);\
    pip install tvb-data tvb-gdist tvb-library

# Compile and Install package for Nest
RUN cd /home/;\
    NAME_SOURCE_NEST=/home/nest-io-dev;\
    PATH_INSTALATION=/usr/lib/nest/;\
    PATH_BUILD=/home/nest-build;\
    export PATH_INSTALATION;\
    export PATH_BUILD;\
    export NAME_SOURCE_NEST;\
    export NEST_DATA_PATH=$PATH_BUILD/pynest;\
    mkdir $PATH_BUILD;\
    cd $PATH_BUILD;\
    cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_INSTALATION $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-python=3;\
    make -j$(nproc);\
    make install
    #make installcheck

ENV PYTHONPATH /usr/lib/nest/lib64/python3.8/site-packages/:/home/:$PYTHONPATH
