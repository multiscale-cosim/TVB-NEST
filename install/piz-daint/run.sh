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

# load the module for all the installation
module load daint-gpu
module load cray-python/3.8.2.1

module load CMake/3.14.5
module load Boost/1.70.0-CrayGNU-20.11-python3
module load GSL/2.5-CrayGNU-20.11
module load python_virtualenv/15.0.3

source /scratch/snx3000/bp000266/co_sim_local/TVB-NEST/lib/site_packages/bin/activate

export PYTHONPATH=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/lib/nest_run/lib64/python3.8/site-packages/:/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/lib/site_packages/lib64/python3.8/site-packages/:/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/lib/site_packages/lib64/python3.8/site-packages/:/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/:$PYTHONPATH

python $DIR/../../nest_elephant_tvb/orchestrator/run.py $1

desactivate

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit

