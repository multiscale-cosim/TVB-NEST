#!/bin/bash
BASEDIR=$(dirname "$0")
mpirun -n 1 python3 $BASEDIR/../simulation_zerlaut.py $1
