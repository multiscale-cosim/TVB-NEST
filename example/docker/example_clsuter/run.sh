module load daint-gpu
module load sarus
module load cray-python
rm -rd case_asynchronous/log case_asynchronous/nest case_asynchronous/tvb case_asynchronous/translation 
salloc -p debug -n 19 -N 6 -C gpu -A ich001 python launcher.py case_asynchronous/parameter.json

