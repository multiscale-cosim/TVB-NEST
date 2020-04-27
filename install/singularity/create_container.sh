#!/bin/bash

rm -f Nest_TVB.simg
sudo /usr/bin/singularity build Nest_TVB.simg Nest_TVB_config.singularity
