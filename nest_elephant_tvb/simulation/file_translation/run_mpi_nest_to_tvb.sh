#!/bin/bash
BASEDIR=$(dirname "$0")
mpirun -n 1 python $BASEDIR/nest_to_tvb.py $1 $2 $3 $4 $5 $6 $7
