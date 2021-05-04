#! /usr/local/bin/bash

module load sarus

srun -n 10 -N 10 sarus run --mpi --mount=type=bind,source=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus,destination=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus/ load/library/PAPER_v1 python3 /scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus/run_LFPY.py $1 'pop_1_' 0 8000 8001 10000 '/v1/'
