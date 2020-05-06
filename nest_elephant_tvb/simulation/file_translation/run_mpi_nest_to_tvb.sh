#!/bin/bash
BASEDIR=$(dirname "$0")
$1 -n 1 python3 $BASEDIR/nest_to_tvb.py $2 $3 $4