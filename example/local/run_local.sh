#! /bin/sh

CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit

rm -rd ./case_up_down/log ./case_up_down/nest ./case_up_down/translation ./case_up_down/tvb
rm -rd ./case_asynchronous/log ./case_asynchronous/nest ./case_asynchronous/translation */tvb
rm -rd ./case_regular_burst/log ./case_regular_burst/nest ./case_regular_burst/translation */tvb

. ./../../tests/init.sh

python3 ../../nest_elephant_tvb/launcher/run_exploration.py ./case_up_down/parameter.json
python3 ../../nest_elephant_tvb/launcher/run_exploration.py ./case_asynchronous/parameter.json
python3 ../../nest_elephant_tvb/launcher/run_exploration.py ./case_regular_burst/parameter.json

#rm -rd ./case_up_down/log ./case_up_down/nest ./case_up_down/translation ./case_up_down/tvb
#rm -rd ./case_asynchronous/log ./case_asynchronous/nest ./case_asynchronous/translation */tvb
#rm -rd ./case_regular_burst/log ./case_regular_burst/nest ./case_regular_burst/translation */tvb

cd $CURRENT_REPERTORY