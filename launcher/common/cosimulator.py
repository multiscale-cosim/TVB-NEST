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
import json

# Co-Simulator imports
import common
import configurations_manager


class CoSimulator:
    """
        Class representing the Co-Simulator tool

    Methods:
    --------
        run(args=None)
            Entry point to the Co-Simulator and executes the main loop of the tool
    """
    # general members
    __args = None
    __configuration_manager = None
    __logs_root_dir = None
    __logger = None
    __launcher = None

    # Environment
    __variables_manager = None

    # XML configuration files managers
    __xml_manager_plan = None
    __xml_manager_actions = None
    __xml_manager_parameters = None

    # dictionaries
    __action_plan_parameters_dict = {}
    __action_plan_variables_dict = {}
    __action_plan_dict = {}

    __actions_popen_args_dict = {}

    __parameters_parameters_dict = {}
    __parameters_variables_dict = {}

    def generate_parameters_json_file(self):
        """
            Dumps into the /path/to/co_sim/results/dir/filename.json file
            the parameters gathered from the parameters XML file

        :return:
            JSON_FILE_ERROR: reporting error during the parameter JSON file
            OK: parameter JSON file was generated properly
        """

        # TO BE DONE: exception management when the file cannot be created

        results_dir = self.__configuration_manager.get_directory('results')
        parameters_json_file = self.__parameters_parameters_dict['CO_SIM_PARAMETERS_JSON_FILENAME']

        with open(os.path.join(results_dir, parameters_json_file), 'w') as json_output_file:
            json.dump(self.__parameters_parameters_dict['CO_SIM_PARAMETERS_JSON_FILE_CONTENT'], json_output_file)

        return common.enums.CoSimulatorReturnCodes.OK

    def run(self, args=None):
        """
            Entry point of the Co-Simulation Co-Simulator tool

        :param args:
            There is no parameters to be used since argparse takes the sys.argv by default

        :return:
            common.enums.CoSimulatorReturnCodes
        """
        ########
        # STEP 1 - Checking command line parameters
        ########
        try:
            self.__args = common.args.arg_parse()
        except SystemExit as e:
            # argument parser has reported some issue with the arguments
            return common.enums.CoSimulatorReturnCodes.PARAMETER_ERROR

        ########
        # STEP 2 - Setting Up the Configuration Manager
        ########
        # TO BE DONE: __logs_root_dir should be set based on environment variable or by using another mechanism
        # e.g. self.__logs_root_dir = os.environ['HOME'] + '/co_sim/logs'
        self.__configuration_manager = configurations_manager.ConfigurationsManager()
        self.__logger = self.__configuration_manager.load_log_configurations(name='co-simulator')
        self.__logger.info('START: Co-Simulation Co-Simulator')

        ########
        # STEP 3 - Setting Up the CO_SIM_* Variables Manager
        ########
        self.__variables_manager = \
            common.variables_manager.VariablesManager(logger=self.__logger)

        # STEP 3.1 - Setting Up the output location (path) for results
        self.__variables_manager.set_value(common.variables.CO_SIM_RESULTS_DIR,
                                           self.__configuration_manager.get_directory('results'))

        ########
        # STEP 4 - Co-Simulation Plan
        ########
        self.__xml_manager_plan = \
            common.xml_manager_plan.XmlManagerPlan(configuration_manager=self.__configuration_manager,
                                                   logger=self.__logger,
                                                   xml_filename=self.__args.action_plan)

        # STEP 4.1 - Dissecting the Co-Simulation Plan XML file
        if not self.__xml_manager_plan.dissect() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.CoSimulatorReturnCodes.XML_ERROR

        # Variables -> Could contain references to Environment variables, e.g. ${HOME}
        # STEP 4.2 - Getting the variables found on the Co-Simulation Plan XML file
        self.__action_plan_variables_dict = self.__xml_manager_plan.get_variables_dict()

        # STEP 4.3 -    Validating the references to the CO_SIM_* variables
        #               by filling up the environment variables dictionary
        if not common.enums.VariablesReturnCodes.VARIABLE_OK == \
                self.__variables_manager.set_variable_values_from_variables_dict(self.__action_plan_variables_dict):
            return common.enums.CoSimulatorReturnCodes.VARIABLE_ERROR

        # Parameters -> Could contain references to CO_SIM_ variables and become new CO_SIM_ variables
        # STEP 4.4 - Getting the parameters found on the Co-Simulation Plan XML file
        self.__action_plan_parameters_dict = self.__xml_manager_plan.get_parameters_dict()

        # STEP 4.5 -    Validating the references to the CO_SIM_* variables on the <parameters> sections
        #               by creating the new CO_SIM_* variables by means of the variables manager
        if not common.enums.ParametersReturnCodes.PARAMETER_OK == \
                self.__variables_manager.create_variables_from_parameters_dict(self.__action_plan_parameters_dict):
            return common.enums.CoSimulatorReturnCodes.PARAMETER_ERROR

        # Action Plan -> ordered and grouped sequence of actions to achieve the Co-Simulation Experiment
        # STEP 4.6 - Getting the action plan per se
        self.__action_plan_dict = self.__xml_manager_plan.get_action_plan_dict()

        ########
        # STEP 5 Co-Simulation Parameters
        ########
        self.__xml_manager_parameters = \
            common.xml_manager_parameters.XmlManagerParameters(configuration_manager=self.__configuration_manager,
                                                               logger=self.__logger,
                                                               xml_filename=self.__args.parameters)

        # STEP 5.1 - Dissecting Co-Simulation Parameters XML file
        if not self.__xml_manager_parameters.dissect() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.CoSimulatorReturnCodes.XML_ERROR

        # STEP 5.2 - Getting the variables found in the Co-Simulation Parameters file
        self.__parameters_variables_dict = self.__xml_manager_parameters.get_variables_dict()

        # STEP 5.3 - Getting the parameters found in the Co-Simulation Parameters file
        self.__parameters_parameters_dict = self.__xml_manager_parameters.get_parameters_dict()

        ########
        # STEP 6 - Co-Simulation Actions (processing the XML configuration files)
        ########
        # STEP 6.1 - Getting the Actions Popen arguments, the CO_SIM_ variables transformation is performed 
        self.__xml_manager_actions = \
            common.xml_manager_actions.XmlManagerActions(configuration_manager=self.__configuration_manager,
                                                         logger=self.__logger,
                                                         environment_variables_manager=self.__variables_manager,
                                                         action_plan=self.__action_plan_dict)
        if not self.__xml_manager_actions.dissect() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.CoSimulatorReturnCodes.XML_ERROR

        self.__actions_popen_args_dict = self.__xml_manager_actions.get_actions_popen_arguments_dict()
        
        ########
        # STEP 7 - Converting Co-Simulation XML parameters into JSON
        ########
        if not self.generate_parameters_json_file() == common.enums.CoSimulatorReturnCodes.OK:
            return common.enums.CoSimulatorReturnCodes.JSON_FILE_ERROR

        ########
        # STEP 8 - Launching action plan
        ########
        self.__launcher = common.Launcher(action_plan_dict=self.__action_plan_dict,
                                          actions_popen_args_dict=self.__actions_popen_args_dict,
                                          configuration_manager=self.__configuration_manager,
                                          logger=self.__logger)
        if not self.__launcher.carry_out_action_plan() == common.enums.LauncherReturnCodes.LAUNCHER_OK:
            return common.enums.CoSimulatorReturnCodes.LAUNCHER_ERROR

        # STEP 99 - Finishing
        self.__logger.info('END: Co-Simulation Co-Simulator')

        return common.enums.CoSimulatorReturnCodes.OK
