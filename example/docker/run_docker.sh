#! /bin/sh

CURRENT_REPERTORY=$(pwd)
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR" || exit
echo "doesn't work missing connection between docker"
set +x
sudo echo "start"
rm -rd ${DIR}/case_up_down/log ${DIR}/case_up_down/nest ${DIR}/case_up_down/translation ${DIR}/case_up_down/tvb
sudo docker run --mount type=bind,source=${DIR}/case_up_down/,target=${DIR}/case_up_down/ local:NEST_TVB_IO_PAPER python3 /home/nest_elephant_tvb/launcher/run_exploration.py ${DIR}/case_up_down/parameter.json
sudo chgrp -R ${USER} ${DIR}/case_up_down; sudo chown -R ${USER} ${DIR}/case_up_down/

rm -rd ${DIR}/case_asynchronous/log ${DIR}/case_asynchronous/nest ${DIR}/case_asynchronous/translation ${DIR}/case_asynchronous/tvb
sudo docker run --mount type=bind,source=${DIR}/case_asynchronous/,target=${DIR}/case_asynchronous/ local:NEST_TVB_IO_PAPER python3 /home/nest_elephant_tvb/launcher/run_exploration.py ${DIR}/case_asynchronous/parameter.json
sudo chgrp -R ${USER} ${DIR}/case_asynchronous; sudo chown -R ${USER} ${DIR}/case_asynchronous/

rm -rd ${DIR}/case_regular_burst/log ${DIR}/case_regular_burst/nest ${DIR}/case_regular_burst/translation ${DIR}/case_regular_burst/tvb
sudo docker run --mount type=bind,source=${DIR}/case_regular_burst/,target=${DIR}/case_regular_burst/ local:NEST_TVB_IO_PAPER python3 /home/nest_elephant_tvb/launcher/run_exploration.py ${DIR}/case_regular_burst/parameter.json
sudo chgrp -R ${USER} ${DIR}/case_regular_burst; sudo chown -R ${USER} ${DIR}/case_regular_burst

cd $CURRENT_REPERTORY