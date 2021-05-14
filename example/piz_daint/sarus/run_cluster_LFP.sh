#! /bin/sh
set -x 

CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

#rm -rd $DIR/case_up_down/LFPY
rm -rd $DIR/case_asynchronous/LFPY
rm -rd $DIR/case_regular_burst/LFPY

#sbatch -N 10 -p normal -C gpu -A ich001 -t 10:0:0 --mail-user=lionel.kusch@univ-amu.fr --job-name=LFP_up_down --output=$DIR/case_up_down/log_LFP.txt --error=$DIR/case_up_down/log_LFP_err.txt ./run_LFPY.sh $DIR/case_up_down/
sbatch -N 10 -p normal -C gpu -A ich001 -t 20:0:0 --mail-user=lionel.kusch@univ-amu.fr --job-name=LFP_asynchronous --output=$DIR/case_asynchronous/log_LFP.txt --error=$DIR/case_asynchronous/log_LFP_err.txt ./run_LFPY.sh $DIR/case_asynchronous/
sbatch -N 10 -p normal -C gpu -A ich001 -t 20:0:0 --mail-user=lionel.kusch@univ-amu.fr --job-name=LFP_regular_bursting --output=$DIR/case_regular_burst/log_LFP.txt --error=$DIR/case_regular_burst/log_LFP_err.txt ./run_LFPY.sh $DIR/case_regular_burst/

cd $CURRENT_REPERTORY
