#! /bin/sh
set -x 

CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

rm -rd $DIR/case_up_down/log $DIR/case_up_down/nest $DIR/case_up_down/transformation $DIR/case_up_down/tvb $DIR/case_up_down/log.txt $DIR/case_up_down/log_err.txt
rm -rd $DIR/case_asynchronous/log $DIR/case_asynchronous/nest $DIR/case_asynchronous/transformation $DIR/case_asynchronous/tvb $DIR/case_asynchronous/log.txt $DIR/case_asynchronous/log_err.txt
rm -rd $DIR/case_regular_burst/log $DIR/case_regular_burst/nest $DIR/case_regular_burst/transformation $DIR/case_regular_burst/tvb $DIR/case_regular_burst/log.txt $DIR/case_regular_burst/log_err.txt

sbatch -N 6 -p normal -C gpu -A ich001 -t 10:0:0 --mail-user=lionel.kusch@univ-amu.fr --job-name=up_down --output=$DIR/case_up_down/log.txt --error=$DIR/case_up_down/log_err.txt ./run_sarus.sh $DIR/../../../ $DIR/case_up_down/parameter.json
sbatch -N 6 -p normal -C gpu -A ich001 -t 10:0:0 --mail-user=lionel.kusch@univ-amu.fr --job-name=asynchronous --output=$DIR/case_asynchronous/log.txt --error=$DIR/case_asynchronous/log_err.txt ./run_sarus.sh $DIR/../../../ $DIR/case_asynchronous/parameter.json
sbatch -N 6 -p normal -C gpu -A ich001 -t 10:0:0 --mail-user=lionel.kusch@univ-amu.fr --job-name=regular_bursting --output=$DIR/case_regular_burst/log.txt --error=$DIR/case_regular_burst/log_err.txt ./run_sarus.sh $DIR/../../../ $DIR/case_regular_burst/parameter.json

cd $CURRENT_REPERTORY
