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
IMAGE=./install/singularity/Nest_TVB_full.simg
#IMAGE=./install/singularity/Nest_TVB.simg
#IMAGE=./install/singularity/Nest_TVB_2.simg

cd ../../
singularity run --app mpi $IMAGE -n 8 python3 test_nest/run_co-sim_test.py $(pwd)/test_nest/test_sing/ 8
cd install/singularity || exit

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
