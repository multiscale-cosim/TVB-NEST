#! /bin/bash

module load daint-mc
module load cray-python/3.8.5.0
module load CMake/3.14.5
module load Boost/1.70.0-CrayGNU-20.11-python3
module load GSL/2.5-CrayGNU-20.11
module load python_virtualenv/15.0.3
module load PyExtensions/python3-CrayGNU-20.11


DIR_LIB=/scratch/snx3000/bp000266/TVB_Nest_paper/lib/
source $DIR_LIB/lib_py/bin/activate
export PATH=$DIR_LIB/lib_py/bin:$DIR_LIB/soft/bin:$PATH
export LD_LIBRARY=$DIR_LIB/lib_py/lib:$DIR_LIB/soft/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$DIR_LIB/lib_py/lib64/python3.8/site-packages/:$DIR/lib_py/lib/python3.8/site-packages/:$DIR_LIB/soft/lib/python/:/scratch/snx3000/bp000266/TVB_Nest_paper/

srun -n 288 -N 8 python3 $(pwd)/run_LFPY.py $1 'pop_1_' 42500 53500 0 8000 8001 2000 '/v1/'

