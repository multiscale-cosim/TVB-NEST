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

# Script needs to be started from the directory it is located in
CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR || exit

PATH_LIB=$DIR/../../lib/
mkdir $PATH_LIB
cd $PATH_LIB

wget http://www.mpich.org/static/downloads/3.4.2/mpich-3.4.2.tar.gz
tar -xf mpich-3.4.2.tar.gz
cd mpich-3.4.2
./configure --prefix=$DIR/../../lib/soft/ --with-device=ch4:ofi
make
make install
cd ..
rm -rdf mpich-3.4.2 mpich-3.4.2.tar.gz

wget https://www.python.org/ftp/python/3.8.10/Python-3.8.10.tar.xz
tar -xf Python-3.8.10.tar.xz
cd Python-3.8.10
./configure --enable-optimizations --enable-shared --prefix=$DIR/../../lib/soft/
make
make install
cd ..
rm -rdf  Python-3.8.10.tar.xz Python-3.8.10

export PATH=$DIR/../../lib/soft/bin:$PATH
export LD_LIBRARY_PATH=$DIR/../../lib/soft/lib/:$LD_LIBRARY_PATH
export PYTHONPATH=$DIR/../../lib/soft/lib/python3.8/:$PYTHONPATH

sh $CURRENT_REPERTORY/../py_venv/create_virtual_python.sh
