#!/bin/bash
BASEDIR=$(dirname "$0")
mpirun -n 1 python $BASEDIR/../simulation_zerlaut.py $1
