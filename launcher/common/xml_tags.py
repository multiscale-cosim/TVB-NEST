# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor
#  license agreements; and to You under the Apache License, Version 2.0. "
#
# Forschungszentrum Jülich
#  Institute: Institute for Advanced Simulation (IAS)
#    Section: Jülich Supercomputing Centre (JSC)
#   Division: High Performance Computing in Neuroscience
# Laboratory: Simulation Laboratory Neuroscience
#       Team: Multi-scale Simulation and Design
#
# ------------------------------------------------------------------------------
# XML Tags used to parse Co-Simulator XML files
# NOTE: these tags may be found in any Co-Simulation XML file
CO_SIM_XML_ROOT_TAG = 'settings'
CO_SIM_XML_TITLE = 'title'
CO_SIM_XML_DESCRIPTION = 'description'
CO_SIM_XML_PARAMETERS = 'parameters'
CO_SIM_XML_PARAMETER_NAME = 'par_name'
CO_SIM_XML_PARAMETER_VALUE = 'par_value'
CO_SIM_XML_VARIABLES = 'variables'
CO_SIM_XML_VARIABLE_NAME = 'var_name'
CO_SIM_XML_VARIABLE_VALUE = 'var_value'
CO_SIM_XML_ARRANGEMENT = 'arrangement'
CO_SIM_XML_ARRANGEMENT_WHAT = 'arr_what'
CO_SIM_XML_ARRANGEMENT_DUTY = 'arr_duty'

# XML Tags used to parse Action Plans XML files
CO_SIM_XML_PLAN_ROOT_TAG = 'co_simulation_action_plan'
CO_SIM_XML_PLAN_TITLE = CO_SIM_XML_TITLE
CO_SIM_XML_PLAN_DESCRIPTION = CO_SIM_XML_DESCRIPTION
CO_SIM_XML_PLAN_VARIABLES = CO_SIM_XML_VARIABLES
CO_SIM_XML_PLAN_PARAMETERS = CO_SIM_XML_PARAMETERS
CO_SIM_XML_PLAN_ARRANGEMENT = CO_SIM_XML_ARRANGEMENT
CO_SIM_XML_PLAN_ACTION_PLAN = 'action_plan'
CO_SIM_XML_PLAN_ACTION_TYPE = 'action_type'
CO_SIM_XML_PLAN_ACTION_XML = 'action_xml'
CO_SIM_XML_PLAN_ACTION_LAUNCH_METHOD = 'action_launch_method'

# XML Tags used to parse Actions XML Files
CO_SIM_XML_ACTION_ROOT_TAG = 'co_simulation_action'
CO_SIM_XML_ACTION_TITLE = CO_SIM_XML_TITLE
CO_SIM_XML_ACTION_DESCRIPTION = CO_SIM_XML_DESCRIPTION
CO_SIM_XML_ACTION = 'action'
CO_SIM_XML_ACTION_LAUNCHER = 'launcher'
CO_SIM_XML_ACTION_LAUNCHER_COMMAND = 'launcher_command'
CO_SIM_XML_ACTION_LAUNCHER_ARGUMENTS = 'launcher_arguments'
CO_SIM_XML_ACTION_LAUNCHER = 'launcher'
CO_SIM_XML_ACTION_PERFORMER = 'performer'
CO_SIM_XML_ACTION_PERFORMER_BINARY = 'performer_binary'
CO_SIM_XML_ACTION_PERFORMER_ARGUMENTS = 'performer_arguments'
CO_SIM_XML_ACTION_ROUTINE = 'routine'
CO_SIM_XML_ACTION_ROUTINE_CODE = 'routine_code'
CO_SIM_XML_ACTION_ROUTINE_ARGUMENTS = 'routine_arguments'


# XML Tags used to parse Co-Simulation Parameters XML files
CO_SIM_XML_CO_SIM_PARAMS_ROOT_TAG = 'co_simulation_parameters'
CO_SIM_XML_CO_SIM_PARAMS_TITLE = CO_SIM_XML_TITLE
CO_SIM_XML_CO_SIM_PARAMS_DESCRIPTION = CO_SIM_XML_DESCRIPTION
CO_SIM_XML_CO_SIM_PARAMS_JSON_FILE = 'parameters_json_file'
CO_SIM_XML_CO_SIM_PARAMS_FILENAME = 'filename'
CO_SIM_XML_CO_SIM_PARAMS_ROOT_OBJECT = 'root_object'
CO_SIM_XML_CO_SIM_PARAMS_PAIRS = 'pairs'
CO_SIM_XML_CO_SIM_PARAMS_PAIR_NAME = 'name'
CO_SIM_XML_CO_SIM_PARAMS_PAIR_VALUE = 'value'
CO_SIM_XML_CO_SIM_PARAMS_PAIR_DATA_TYPE = 'data_type'





