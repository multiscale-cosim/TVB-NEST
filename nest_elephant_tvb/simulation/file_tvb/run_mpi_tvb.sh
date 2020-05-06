#!/bin/bash
BASEDIR=$(dirname "$0")
$1 -n 1 python3 $BASEDIR/../simulation_zerlaut.py $2
