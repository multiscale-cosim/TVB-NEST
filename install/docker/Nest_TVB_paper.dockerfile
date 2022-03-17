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

# get compiler and access to web interface
RUN apt-get update;\
    apt-get install -y g++=4:8.3.0-1 gcc=4:8.3.0-1 gfortran=4:8.3.0-1 make=4.2.1-1.2 strace=4.26-0.2 wget=1.20.1-1.1 git=1:2.20.1-2+deb10u3

# install python
RUN  apt-get install -y build-essential=12.6 cmake=3.13.4-1 zlib1g-dev=1:1.2.11.dfsg-1 libltdl-dev=2.4.6-9\
     libncurses5-dev=6.1+20181013-2+deb10u2 libgdbm-dev=1.18.1-4 libreadline-dev=7.0-5 \
     libnss3=2:3.42.1-1+deb10u3 \
     libnss3-dev=2:3.42.1-1+deb10u3 libssl-dev=1.1.1d-0+deb10u7 libsqlite3-dev=3.27.2-3+deb10u1 libgl1-mesa-glx=18.3.6-2+deb10u1 \
     libffi-dev=3.2.1-9 libgsl-dev=2.5+dfsg-6 libbz2-dev=1.0.6-9.2~deb10u1 curl=7.64.0-4+deb10u2;\
     cd /root ;\
     curl -O https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tar.xz ;\
     tar -xf Python-3.8.10.tar.xz ;\
     cd Python-3.8.10 ;\
     ./configure --enable-optimizations --enable-shared ;\
     make ;\
     make altinstall ;\
     cd .. ;\
     rm -rdf  Python-3.8.10.tar.xz Python-3.8.10

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib/

# install pip
RUN cd /root ;\
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py;\
    python3.8 get-pip.py;\
    rm get-pip.py;\
    pip install --upgrade pip==21.1.2

# install MPI
RUN wget -q --no-check-certificate http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz;\
    tar xf mpich-3.1.4.tar.gz;\
    cd mpich-3.1.4;\
    ./configure --disable-fortran --enable-fast=all,O3 --prefix=/usr;\
    make -j$(nproc);\
    make install;\
    cd ..;\
    rm -rdf mpich-3.1.4.tar.gz mpich-3.1.4

# Install the dependance for Nest
RUN pip install nose==1.3.7;\
    pip install numpy==1.20.3 cython==0.29.23 Pillow==8.2.0;\
    pip install mpi4py==3.0.3;\
    apt-get install -y liblapack-dev;\
    pip install scipy==1.6.3 ;\
    pip install elephant==0.10.0;\
    pip install matplotlib==3.4.2;\
    pip install networkx==2.5.1;\
    pip install jupyter==1.0.0;\
    pip install vtk==9.0.1;\
    pip install h5py==3.2.1;\
    pip install cycler==0.10.0;\
    pip install jupyter==1.0.0;\
    pip install plotly==5.1.0

# install TVB
RUN apt-get install -y llvm-dev=1:7.0-47 llvm=1:7.0-47;\
    export LLVM_CONFIG=/usr/bin/llvm-config;\
    pip install tvb-data==2.0 tvb-gdist==2.0.0 tvb-library==2.0.10

# install parameters
RUN git clone https://github.com/NeuralEnsemble/parameters;\
    cd parameters;\
    python3.8 setup.py install;\
    cd .. ;\
    rm -rd parameters

# install neuron
RUN apt-get install -y bison=2:3.3.2.dfsg-1 flex=2.6.4-6.2 libxcomposite-dev=1:0.4.4-2

RUN git clone https://github.com/neuronsimulator/nrn.git;\
    cd nrn;\
    git checkout 8.0.0;\
    mkdir build;\
    cd build;\
    cmake .. \
    -DNRN_ENABLE_INTERVIEWS=OFF \
    -DNRN_ENABLE_MPI=OFF \
    -DNRN_ENABLE_RX3D=OFF \
    -DCMAKE_INSTALL_PREFIX=/usr/local/nrn;\
    cmake --build . --parallel 8 --target install;\
    cd ../..;\
    rm -rdf nrn

ENV PATH=/usr/local/nrn/bin:$PATH

ENV PYTHONPATH=/usr/local/nrn/lib/python:$PYTHONPATH

# install LPFy
RUN pip install lfpykit==0.3;\
    pip install MEAutility==1.4.9;\
    pip install LFPy==2.2.1

# install HybridLFPy from github
RUN git clone --branch nest-3-lio https://github.com/lionelkusch/hybridLFPy.git;\
    cd hybridLFPy;\
    python3.8 setup.py install;\
    cd .. ;\
    rm -rd hybridLFPy


# Compile and Install package for Nest
COPY  ./nest-io-dev /home/nest-io-dev

RUN cd /home/;\
    NAME_SOURCE_NEST=/home/nest-io-dev;\
    PATH_INSTALATION=/usr/lib/nest/;\
    PATH_BUILD=/home/nest-simulator-build;\
    export PATH_INSTALATION;\
    export PATH_BUILD	;\
    export NAME_SOURCE_NEST;\
    export NEST_DATA_PATH=$PATH_BUILD/pynest;\
    export PYTHONPATH=$PATH_INSTALATION/lib/python3.8/site-packages:$PYTHONPATH;\
    export PATH=$PATH:$PATH_INSTALATION/bin;\
    mkdir $PATH_BUILD;\
    cd $PATH_BUILD;\
    cmake -DCMAKE_INSTALL_PREFIX:PATH=$PATH_INSTALATION $NAME_SOURCE_NEST -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-readline=On -Dwith-ltdl=ON -Dwith-python=ON -Dcythonize-pynest=ON ;\
    make;\
    make install
    #make installcheck

# Copy files of the project
COPY  ./nest_elephant_tvb /home/nest_elephant_tvb
COPY  ./analyse /home/analyse
COPY  ./timer /home/timer

# initialisation of special synapse for Neuron
RUN cd /home/analyse/LFPY;\
    nrnivmodl

# create python3 executable
RUN ln -s /usr/local/bin/python3.8 /usr/local/bin/python3

ENV PYTHONPATH=/usr/lib/nest/lib/python3.8/site-packages/:/home/:$PYTHONPATH
ENV PATH=/usr/lib/nest/:$PATH

