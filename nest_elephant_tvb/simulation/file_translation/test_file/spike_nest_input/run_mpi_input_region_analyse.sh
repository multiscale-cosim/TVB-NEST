#!/bin/bash
BASEDIR=$(dirname "$0")
mpirun -n 1 python $BASEDIR/input_region_activity.py $1 $2
