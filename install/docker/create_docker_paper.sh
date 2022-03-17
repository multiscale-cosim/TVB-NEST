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

# copy the folder for compiling in the docker
cp -r  ../../nest-io-dev .
cp -r  ../../nest_elephant_tvb .
cp -r  ../../analyse .
cp -r  ../../timer .
sudo docker rmi local:NEST_TVB_IO_PAPER_TIMER
sudo docker build -t local:NEST_TVB_IO_PAPER_TIMER --no-cache -f Nest_TVB_paper.dockerfile .
rm -rd nest-io-dev analyse nest_elephant_tvb timer

# return to the calling repertory
cd "${CURRENT_REPERTORY}" || exit
