PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../../../co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../../../co_simulation/co-simulation-tvb-nest/lib/nest_run_3/lib/python3.6/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=$PATH:${PWD}/../../../co_simulation/co-simulation-tvb-nest/venv/


for i in {10,40,100,400,1000,4000,10000}
do
  python3 ./run_co-sim_neuron.py './test_file/benchmark/' 0.0 1000.0 $i
done