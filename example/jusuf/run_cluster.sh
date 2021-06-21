#! /bin/sh
set -x 

CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

rm -rd $DIR/case_asynchronous/log $DIR/case_asynchronous/nest $DIR/case_asynchronous/translation $DIR/case_asynchronous/tvb $DIR/case_asynchronous/log.txt $DIR/case_asynchronous/log_err.txt

sbatch --account=training2115  -p batch -N 2 -t 0:5:0 --mail-user=lionel.kusch@univ-amu.fr --job-name=test --output=$DIR/case_asynchronous/log.txt --error=$DIR/case_asynchronous/log_err.txt ./run_example.sh $DIR  $DIR/../../ $DIR/case_asynchronous/parameter.json

cd $CURRENT_REPERTORY
