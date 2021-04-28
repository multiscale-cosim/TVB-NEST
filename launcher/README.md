Prerequisite:

`export PYTHONPATH=/path/to/TVB-NEST/configuration_manager`

e.g.

`export PYTHONPATH=/home/user/TVB-NEST/configuration_manager/`

Launching a Co-Simulation plan:

`python3 /path/to/launcher/main.py --global-settings /path/to/co_simulation_global_Settings.xml --action-plan /path/to/plans/action_plan.xml --parameters /path/to/parameters/co_simulation_parameters.xml`

e.g.

`python3 ~/TVB-NEST/launcher/main.py --global-settings ~/TVB-NEST/configuration_manager/global_settings.xml --action-plan ~/TVB-NEST/launcher/plans/translator_nest_to_tvb_on_local.xml --parameters ~/TVB-NEST/launcher/parameters/nest_to_tvb_parameters.xml`



