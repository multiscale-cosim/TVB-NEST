#!/bin/bash
BASEDIR=$(dirname "$0")
$1 -n 1 python3 $BASEDIR/nest_save_hist.py $2 $3 $4 $5
