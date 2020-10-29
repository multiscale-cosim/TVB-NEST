CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd $DIR || exit

. ../init.sh
echo "python path " $PYTHONPATH $CLUSTER

salloc --partition=dp-dam -N 1 python3 ${CURRENT_REPERTORY}/run_co-sim_neuron.py './test_file/benchmark/' 0.0 1000.0 1000

#salloc --partition=dp-cn -N 2 : --partition=dp-dam -N 4

#for i in {10,40,100,400,1000,4000,10000}
#do
#  python3 ./run_co-sim_neuron.py './test_file/benchmark/' 0.0 1000.0 $i
#done
