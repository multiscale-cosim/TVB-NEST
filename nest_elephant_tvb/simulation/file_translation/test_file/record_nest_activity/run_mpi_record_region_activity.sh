#!/bin/bash
BASEDIR=$(dirname "$0")
mpirun -n 1 python $BASEDIR/record_region_activity.py $1 $2
