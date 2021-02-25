#!/usr/bin/env python
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
#       Team: Multiscale Simulation and Design
#
#   Date: 2021.02.16
# ------------------------------------------------------------------------------
import os
import common
import configurations_manager
# import xml
import json


class Launcher:
    """
        Class representing the co-simulation launcher tool

    Methods:
    --------
        run(args=None)
            Entry point to the launcher and executes the main loop of the tool
    """
    # general members
    __args = None
    __configuration_manager = None
    __logs_root_dir = None
    __logger = None

    # XML validators
    __co_sim_parameters_validator = None
    __co_sim_plan_validator = None

    # dictionaries
    __action_plan_parameters_dict = {}
    __action_plan_variables_dict = {}
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

        with open(results_dir+'/'+parameters_json_file, 'w') as json_output_file:
            json.dump(self.__parameters_parameters_dict['CO_SIM_PARAMETERS_JSON_FILE_CONTENT'], json_output_file)

        return common.enums.LauncherReturnCodes.OK

    def run(self, args=None):
        """
            Entry point of the Co-Simulation Launcher tool

        :param args:
            There is no parameters to be used since argparse takes the sys.argv by default

        :return:
            common.enums.LauncherReturnCodes
        """
        ########
        # STEP 1 - Checking command line parameters
        ########
        try:
            self.__args = common.args.arg_parse()
        except SystemExit as e:
            # argument parser has reported some issue with the arguments
            return common.enums.LauncherReturnCodes.PARAMETER_ERROR

        ########
        # STEP 2 - Setting Up the Configuration Manager
        ########
        # TO BE DONE: __logs_root_dir should be set based on environment variable or by using another mechanism
        # e.g. self.__logs_root_dir = os.environ['HOME'] + '/co_sim/logs'
        self.__configuration_manager = configurations_manager.ConfigurationsManager()
        self.__logger = self.__configuration_manager.load_log_configurations(name='launcher')
        self.__logger.info('START: Co-Simulation Launcher')

        ########
        # STEP 3 - Co-Simulation Plan
        ########
        self.__co_sim_plan_validator = \
            common.xml_managers.CoSimulationPlanXmlManager(configuration_manager=self.__configuration_manager,
                                                           logger=self.__logger,
                                                           xml_filename=self.__args.action_plan)

        # STEP 3.1 - Validating Co-Simulation Plan XML file
        if not self.__co_sim_plan_validator.dissect() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.LauncherReturnCodes.XML_ERROR

        # STEP 3.2 - Getting the parameters found on the Co-Simulation Plan XML file
        self.__action_plan_parameters_dict = self.__co_sim_plan_validator.get_parameters_dict()

        # STEP 3.3 - Getting the variables found on the Co-Simulation Plan XML file
        self.__action_plan_variables_dict = self.__co_sim_plan_validator.get_variables_dict()

        ###################################
        # STEP 4 Co-Simulation Parameters #
        ###################################
        self.__co_sim_parameters_validator = \
            common.xml_managers.CoSimulationParametersXmlManager(configuration_manager=self.__configuration_manager,
                                                                 logger=self.__logger,
                                                                 xml_filename=self.__args.parameters)

        # STEP 4.1 - Validating Co-Simulation Parameters XML file
        if not self.__co_sim_parameters_validator.dissect() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.LauncherReturnCodes.XML_ERROR

        # STEP 4.2 - Getting the parameters found on the Co-Simulation Plan XML file
        self.__parameters_parameters_dict = self.__co_sim_parameters_validator.get_parameters_dict()

        # STEP 4.3 - Getting the variables found on the Co-Simulation Plan XML file
        self.__parameters_variables_dict = self.__co_sim_parameters_validator.get_variables_dict()

        # STEP 5 - Converting Co-Simulation XML parameters into JSON
        if not self.generate_parameters_json_file() == common.enums.LauncherReturnCodes.OK:
            return common.enums.LauncherReturnCodes.JSON_FILE_ERROR

        # STEP 6 - Launching action plan
        # TO BE DONE

        # STEP 99 - Finishing
        self.__logger.info('END: Co-Simulation Launcher')

        return common.enums.LauncherReturnCodes.OK
