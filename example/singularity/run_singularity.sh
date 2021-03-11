#! /bin/sh

CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

rm -rd */log */nest */translation */tvb

python3 ../../nest_elephant_tvb/orchestrator/run_exploration.py ./case_up_down/parameter.json
python3 ../../nest_elephant_tvb/orchestrator/run_exploration.py ./case_asynchronous/parameter.json
python3 ../../nest_elephant_tvb/orchestrator/run_exploration.py ./case_regular_burst/parameter.json

rm -rd */log */nest */translation */tvb

cd $CURRENT_REPERTORY