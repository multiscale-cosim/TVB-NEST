PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../../../co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../../../co_simulation/co-simulation-tvb-nest/lib/nest_run/lib/python3.6/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=$PATH:${PWD}/../../../co_simulation/co-simulation-tvb-nest/venv/

for i in {1..10}
do
  python3 ./run_co-sim_2.py './test_file/new_2/10000/' 0.0 1000.0 $i
done