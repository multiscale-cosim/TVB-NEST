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
cd "$DIR" || exit

# choice of the image
if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit
fi
if [ $1 -eq 0 ]
then
  IMAGE=./install/singularity/Nest_TVB_paper.simg
  echo ' test image paper Nest and TVB'
elif [ $1 -eq 1 ]
then
  IMAGE=./install/singularity/Nest_TVB_paper_alpine.simg
  echo ' test image paper alpine OS Nest and TVB'
else
  echo ' No image to test '
  exit
fi

# launch the test
cd ../../
mkdir $(pwd)/tests/test_singularity/
singularity run --app python $IMAGE ./tests/run_co-sim_test.py $(pwd)/tests/test_file/test_singularity/ 4 4 false
rm -rd $(pwd)/tests/test_singularity/
cd install/singularity || exit

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
