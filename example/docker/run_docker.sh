#! /bin/sh

CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit
echo "doesn't work missing connection between docker"
sudo --preserve-env=DIR,PATH -- sh -c "cd $DIR &&rm -rd */log */nest */translation */tvb"
#
sudo --preserve-env=DIR,PATH -- sh -c "cd $DIR && python3 ../../nest_elephant_tvb/launcher/run_exploration.py ./case_up_down/parameter.json"
sudo --preserve-env=DIR,PATH -- sh -c "cd $DIR && python3 ../../nest_elephant_tvb/launcher/run_exploration.py ./case_asynchronous/parameter.json"
sudo --preserve-env=DIR,PATH -- sh -c "cd $DIR && python3 ../../nest_elephant_tvb/launcher/run_exploration.py ./case_regular_burst/parameter.json"
#
#sudo --preserve-env=DIR,PATH -- sh -c "cd $DIR && rm -rd */log */nest */translation */tvb"

cd $CURRENT_REPERTORY