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

# Co-Simulator Imports
import common


class VariablesManager(object):
    """
        Manages the variables related to the run-time environment
    """
    __logger = None

    def __init__(self, logger=None):
        self.__logger = logger

        self.__dict = {
            # Actions XML files location
            common.variables.CO_SIM_ACTIONS_DIR: {
                common.constants.CO_SIM_VARIABLE_DESCRIPTION: 'Path to actions XML files',
                common.constants.CO_SIM_VARIABLE_VALUE: None},
            # Empty, TO BE USED AS A FAKE VALUE
            common.variables.CO_SIM_EMPTY: {
                common.constants.CO_SIM_VARIABLE_DESCRIPTION: 'empty string',
                common.constants.CO_SIM_VARIABLE_VALUE: ''},
            # Execution Environment <Local|Cluster>
            common.variables.CO_SIM_EXECUTION_ENVIRONMENT: {
                common.constants.CO_SIM_VARIABLE_DESCRIPTION: 'Co-Simulator Execution Environment',
                common.constants.CO_SIM_VARIABLE_VALUE: None},
            # Results Output Directory
            common.variables.CO_SIM_RESULTS_DIR: {
                common.constants.CO_SIM_VARIABLE_DESCRIPTION: 'Results files directory location',
                common.constants.CO_SIM_VARIABLE_VALUE: None},
            # Routines Directory Path
            common.variables.CO_SIM_ROUTINES_DIR: {
                common.constants.CO_SIM_VARIABLE_DESCRIPTION: 'Co-Simulation Routines directory location',
                common.constants.CO_SIM_VARIABLE_VALUE: None}, }

    def get_value(self, variable_name=None):
        """

        :param variable_name: The environment variable name which the value is being gotten (requested)
        :return: The value of the passed variable name
        """
        return self.__dict[variable_name][common.constants.CO_SIM_VARIABLE_VALUE]

    def set_value(self, variable_name=None, variable_value=None):
        """

        :param variable_value:
        :param variable_name:
        :return:
        """
        try:
            self.__dict[variable_name][common.constants.CO_SIM_VARIABLE_VALUE] = variable_value
        except KeyError:
            self.__logger.error('{} has not been declared in the variable manager yet'.format(variable_name))
            raise common.exceptions.CoSimVariableNotFound(co_sim_variable_name=variable_name)
            return None

        return self.__dict[variable_name]

    def set_variable_values_from_variables_dict(self, variables_dictionary_source=None):
        """

        :param variables_dictionary_source: Dictionary containing Co-Simulation Variables (CO_SIM_*)
        :return:

        """
        for key, value in variables_dictionary_source.items():
            try:
                self.__dict[key][common.constants.CO_SIM_VARIABLE_VALUE] = value
            except KeyError:
                self.__logger.error('{} is not a defined Co-Simulator variable'.format(key))
                return common.enums.VariablesReturnCodes.VARIABLE_NOT_OK

        return common.enums.VariablesReturnCodes.VARIABLE_OK

    def create_variables_from_parameters_dict(self, input_dictionary=None):
        """
            Transforms the referenced variables names into its values based on CO_SIM_* variables.

            CO_SIM_* variables are those referencing a value in the same XML configuration file.
                e.g.
                    CO_SIM_RUNTIME_RESULTS_DIR -> represents the output path where the results files
                                                    will be written/read.
                    and could be referenced as follows:
                    <var_186>
                        <var_name>CO_SIM_VISUALIZATION_FILES_OUTPUT_PATH</var_name>
                        <var_value>CO_SIM_RUNTIME_RESULTS_DIR/visualizer</var_value>
                    </var_186>

            Environment variables are those defined on the system where the Co-Simulation process is being run.
                e.g.
                        ${CO_SIM_TVB_NEST_PATH} -> represents the path where the TVB_NEST repository is located.
                    and could be referenced as follows:
                    <var_194>
                        <var_name>CO_SIM_XML_ACTIONS_DIR</var_name>
                        <var_value>${CO_SIM_TVB_NEST_PATH}/co_simulator/actions</var_value>
                    </var_194>

        :param input_dictionary:
            The private attribute object reference of the dictionary where the
            variables will be transformed into its values

        :return:
            XML_OK: All the referenced variables in the dictionary where properly
                    interchanged by its values
            XML_CO_SIM_VARIABLE_ERROR: The value for a referenced variable could not been obtained
        """
        for key, value in input_dictionary.items():
            # transforming the CO_SIM_ references into its values
            try:
                runtime_variable_value = \
                    common.utils.transform_co_simulation_variables_into_values(variables_manager=self,
                                                                               functional_variable_value=value)
            except common.exceptions.CoSimVariableNotFound as CoSimVariableNotFound:
                self.__logger.error(CoSimVariableNotFound)
                return common.enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR

            # creating the new CO_SIM_ variable
            self.__dict[key] = {common.constants.CO_SIM_VARIABLE_DESCRIPTION: 'created on run time',
                                common.constants.CO_SIM_VARIABLE_VALUE: runtime_variable_value}
        return common.enums.ParametersReturnCodes.PARAMETER_OK
