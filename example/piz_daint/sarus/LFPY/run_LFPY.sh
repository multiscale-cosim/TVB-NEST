#! /usr/local/bin/bash

module load sarus

#srun -n 1 -N 1 -p debug -C gpu -A ich001 sarus run --mpi --mount=type=bind,source=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus,destination=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus/ load/library/PAPER_v1 python3 /scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus/LFPY/run_LFPY.py /scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus/case_asynchronous_test/ 'pop_1_' 0 100 8001 8100 '/small_init_test_2/'
srun -n 4 -N 4 -p debug -C gpu -A ich001 sarus run --mpi --mount=type=bind,source=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus,destination=/scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus/ load/library/PAPER_v1 python3 /scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus/LFPY/run_LFPY.py /scratch/snx3000/bp000266/co_sim_local/TVB-NEST/example/piz_daint/sarus/LFPY/ 'pop_1_' 0 8000 8001 10000 '/small_init_test_2/'
