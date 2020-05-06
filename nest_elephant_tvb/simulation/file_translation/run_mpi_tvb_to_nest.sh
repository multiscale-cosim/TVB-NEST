#!/bin/bash
BASEDIR=$(dirname "$0")
$1 -n 1 python3 $BASEDIR/tvb_to_nest.py $2 $3 $4 $5
