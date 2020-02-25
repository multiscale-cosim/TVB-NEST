#!/bin/bash
BASEDIR=$(dirname "$0")
mpirun -n 1 python $BASEDIR/tvb_to_nest.py $1 $2 $3 $4 $5 $6
