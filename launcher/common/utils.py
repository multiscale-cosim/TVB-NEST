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
import os
import re

# Co-Simulator imports
import common


def transform_co_simulation_variables_into_values(variables_manager=None, functional_variable_value=None):
    """
        Replaces the {CO_SIM_<something>} references into the run-time values of such variables

    :param
        functional_variable_value: String containing reference(s) to CO_SIM_* variable(s)

    :return:
        transformed_variable_value: Transformed string containing
                                the CO_SIM_ variable values of the referenced CO_SIM_ variables
    """
    transformed_variable_value = ''

    # finding co_simulation variables
    split_variable_list = re.split(common.constants.CO_SIM_REGEX_CO_SIM_VARIABLE, functional_variable_value)

    next_piece_is_an_co_simulation_variable_name = False
    next_piece_is_the_closing_curly_brace = False
    for current_piece in split_variable_list:
        if current_piece == '{CO_SIM_':
            next_piece_is_an_co_simulation_variable_name = True
            continue  # goto for it

        elif next_piece_is_an_co_simulation_variable_name:
            next_piece_is_an_co_simulation_variable_name = False
            next_piece_is_the_closing_curly_brace = True  # after processing the co_simulation variable a '}' is expected
            try:
                # getting the co_simulation variable value from the variables manager
                transformed_variable_value += variables_manager.get_value('CO_SIM_'+current_piece)
            except KeyError:
                transformed_variable_value = ''
                raise common.exceptions.CoSimVariableNotFound(current_piece)
                break
        elif next_piece_is_the_closing_curly_brace:
            next_piece_is_the_closing_curly_brace = False
            # bypassing the closing curly brace char
            continue  # carry on the string processing
        else:
            # just add the split element
            transformed_variable_value += current_piece

    return transformed_variable_value


def transform_environment_variables_into_values(functional_variable_value=None):
    """
        Replaces the ${ENV_VAR_NAME} references into the run-time values of such variables

    :param
        functional_variable_value: String containing reference to environment variables

    :return:
        transformed_variable_value: Transformed string containing
                                the run-time values of the referenced environment variables
    """
    transformed_variable_value = ''

    # finding environment variables
    split_variable_list = re.split(common.constants.CO_SIM_REGEX_ENVIRONMENT_VARIABLE, functional_variable_value)

    next_piece_is_an_environment_variable_name = False
    next_piece_is_the_closing_curly_brace = False
    for current_piece in split_variable_list:
        if current_piece == '${':
            next_piece_is_an_environment_variable_name = True
            continue  # goto for it

        elif next_piece_is_an_environment_variable_name:
            next_piece_is_an_environment_variable_name = False
            next_piece_is_the_closing_curly_brace = True  # after processing the environment variable a '}' is expected
            try:
                # getting the environment variable value from the running system
                transformed_variable_value += os.environ[current_piece]
            except KeyError:
                transformed_variable_value = ''
                raise common.exceptions.EnvironmentVariableNotSet(current_piece)
                break
        elif next_piece_is_the_closing_curly_brace:
            next_piece_is_the_closing_curly_brace = False
            # bypassing the closing curly brace char
            continue  # carry on the string processing
        else:
            # just add the split element
            transformed_variable_value += current_piece

    return transformed_variable_value
