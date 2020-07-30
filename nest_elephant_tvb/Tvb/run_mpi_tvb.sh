#!/bin/bash
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

BASEDIR=$(dirname "$0")
$1 -n 1 python3 $BASEDIR/simulation_Zerlaut.py $2 $3
