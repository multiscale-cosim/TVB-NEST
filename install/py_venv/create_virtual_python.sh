#!/bin/bash

pip3 install virtualenv
virtualenv -p python3 --system-site-packages tvb_nest_lib
source tvb_nest_lib/bin/activate

pip install nose
pip install numpy cython Pillow
pip install matplotlib
pip install mpi4py
pip install scipy 
pip install elephant

pip install tvb-data tvb-gdist tvb-library

deactivate
