PACKAGE=${PWD}/../   # folder of co-simulation-tvb-nest
PYTHONLIB=${PWD}/../../../co_simulation/co-simulation-tvb-nest/venv/lib/python3.6/site-packages/ # folder with python library
REPERTORY_LIB_NEST=${PWD}/../../../co_simulation/co-simulation-tvb-nest/lib/nest_run_3/lib/python3.6/site-packages/ # folder with py-nest
export PYTHONPATH=$PYTHONPATH:$PACKAGE:$PYTHONLIB:$REPERTORY_LIB_NEST
export PATH=$PATH:${PWD}/../../../co_simulation/co-simulation-tvb-nest/venv/


for i in {10,12,13,15,18,20,23,27,31,36,41,47,54,63,72,83,95,110,126,146,168,193,222,256,295,339,391,450,518,596,687,791,910,1048,1207,1389,1600,1842,2121,2442,2812,3237,3728,4292,4942,5690,6551,7543,8685,10000}
do
  python3 ./run_co-sim_neuron.py './test_file/benchmark_final/' 0.0 1000.0 $i
  python3 ./run_co-sim_neuron_1.py './test_file/benchmark_final/' 0.0 1000.0 $i
  python3 ./run_co-sim_neuron_inst.py './test_file/benchmark_final/' 0.0 1000.0 $i
done