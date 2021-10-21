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
from default_directories_enum import DefaultDirectories
from common.launching_manager import LaunchingManager

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
    __arranger = None
    __configuration_manager = None
    __logs_root_dir = None
    __logger = None
    __launcher = None

    # Environment
    __variables_manager = None

    # XML configuration files managers
    __actions_xml_manager = None
    __parameters_xml_manager = None
    __plan_xml_manager = None

    # dictionaries
    __action_plan_parameters_dict = {}
    __action_plan_variables_dict = {}
    __action_plan_dict = {}
    __items_to_be_arranged = {}

    __actions_popen_args_dict = {}

    __parameters_parameters_dict = {}
    __parameters_parameters_for_json_file_dict = {}
    __parameters_variables_dict = {}

    __logger_settings = {}

    def generate_parameters_json_file(self):
        """
            Dumps into the /path/to/co_sim/results/dir/filename.json file
            the parameters gathered from the parameters XML file

        :return:
            JSON_FILE_ERROR: reporting error during the parameter JSON file
            OK: parameter JSON file was generated properly
        """
        # TO BE DONE: exception management when the file cannot be created

        results_dir = self.__configuration_manager.get_directory(DefaultDirectories.RESULTS)
        json_output_filename = \
            self.__parameters_parameters_for_json_file_dict[common.xml_tags.CO_SIM_XML_CO_SIM_PARAMS_FILENAME]
        json_output_path_filename = os.path.join(results_dir, json_output_filename)

        try:
            with open(json_output_path_filename, 'w') as json_output_file:
                json.dump(
                    self.__parameters_parameters_for_json_file_dict[common.xml_tags.CO_SIM_XML_CO_SIM_PARAMS_JSON_FILE],
                    json_output_file)
        except OSError:
            self.__logger.error('{} cannot be created, OS error'.format(json_output_path_filename))
            return common.enums.CoSimulatorReturnCodes.JSON_FILE_OS_ERROR

        self.__logger.info('Co-Simulation parameters were transformed successfully')
        self.__logger.info('Co-Simulation parameters: {}'.format(json_output_path_filename))
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

        ####################
        # instantiate configuration manager
        self.__configuration_manager = configurations_manager.ConfigurationsManager()
        
        # get path to setup the output directories
        default_dir = self.__configuration_manager.get_configuration_settings(
            'output_directory', self.__args.global_settings)
        
        # setup default directories (Output, Output/Results, Output/Logs,
        # Output/Figures, Output/Monitoring_DATA)
        self.__configuration_manager.setup_default_directories(default_dir['output_directory'])

        # load common settings for the logging
        self.__logger_settings = self.__configuration_manager.get_configuration_settings(
                            'log_configurations', self.__args.global_settings)
                            
        self.__logger = self.__configuration_manager.load_log_configurations(
                            name=__name__, log_configurations=self.__logger_settings)
        self.__logger.info('Co-Simulator STEP 2 done, configuration manager started')

        ########
        # STEP 3 - Setting Up CO_SIM_* Variables by means of the Variables Manager
        ########
        self.__logger.info('Co-Simulator STEP 3 running')
        self.__variables_manager = \
            common.variables_manager.VariablesManager(logger=self.__logger)

        # STEP 3.1 - Setting Up the output location (path) for results
#        self.__variables_manager.set_value(common.variables.CO_SIM_RESULTS_DIR,
 #                                          self.__configuration_manager.get_directory('results'))
        self.__variables_manager.set_value(common.variables.CO_SIM_RESULTS_DIR,
                                           self.__configuration_manager.get_directory(DefaultDirectories.RESULTS))


        # STEP 3.2 - Setting Up the launcher command based on the environment

        self.__logger.info(
            f'Co-Simulator STEP 3 done, Co-Simulation results location: '
            f'{self.__variables_manager.get_value(common.variables.CO_SIM_RESULTS_DIR)}')

        ########
        # STEP 4 - Co-Simulation Plan
        ########
        self.__logger.info('Co-Simulator STEP 4, dissecting Co-Simulation Action Plan')
        self.__plan_xml_manager = \
            common.plan_xml_manager.PlanXmlManager(configuration_manager=self.__configuration_manager,
                                                   logger=self.__logger,
                                                   xml_filename=self.__args.action_plan)

        # STEP 4.1 - Dissecting the Co-Simulation Plan XML file
        if not self.__plan_xml_manager.dissect() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.CoSimulatorReturnCodes.XML_ERROR

        # Variables -> Could contain references to Environment variables, e.g. ${HOME}
        # STEP 4.2 - Getting the variables found on the Co-Simulation Plan XML file
        self.__action_plan_variables_dict = self.__plan_xml_manager.get_variables_dict()

        # STEP 4.3 -    Validating the references to the CO_SIM_* variables
        #               by filling up the environment variables dictionary
        if not common.enums.VariablesReturnCodes.VARIABLE_OK == \
               self.__variables_manager.set_co_sim_variable_values_from_variables_dict(
                   self.__action_plan_variables_dict):
            return common.enums.CoSimulatorReturnCodes.VARIABLE_ERROR

        # Parameters -> Could contain references to CO_SIM_ variables and become new CO_SIM_ variables
        # STEP 4.4 - Getting the parameters found on the Co-Simulation Plan XML file
        self.__action_plan_parameters_dict = self.__plan_xml_manager.get_parameters_dict()

        # STEP 4.5 -    Validating the references to the CO_SIM_* variables on the <parameters> sections
        #               by creating the new CO_SIM_* variables by means of the variables manager
        if not common.enums.ParametersReturnCodes.PARAMETER_OK == \
               self.__variables_manager.create_variables_from_parameters_dict(self.__action_plan_parameters_dict):
            return common.enums.CoSimulatorReturnCodes.PARAMETER_ERROR

        # STEP 4.6 - Creates Co-Simulation variables based on the information
        #            set on the variables and parameters sections of the processing XML action plan file
        if not common.enums.VariablesReturnCodes.VARIABLE_OK == \
               self.__variables_manager.create_co_sim_run_time_variables(self.__action_plan_variables_dict,
                                                                         self.__action_plan_parameters_dict):
            return common.enums.CoSimulatorReturnCodes.VARIABLE_ERROR

        # Action Plan -> ordered and grouped sequence of actions to achieve the Co-Simulation Experiment
        # STEP 4.7 - Getting the action plan per se
        self.__action_plan_dict = self.__plan_xml_manager.get_action_plan_dict()

        self.__logger.info('{} -> {}'.format(common.variables.CO_SIM_ACTIONS_DIR,
                                             self.__variables_manager.get_value(common.variables.CO_SIM_ACTIONS_DIR)))
        self.__logger.info('{} -> {}'.format(common.variables.CO_SIM_ROUTINES_DIR,
                                             self.__variables_manager.get_value(common.variables.CO_SIM_ROUTINES_DIR)))
        self.__logger.info('Co-Simulator STEP 4 done')

        ########
        # STEP 5 - Processing Co-Simulation Parameters
        ########
        self.__logger.info('Co-Simulator STEP 5, dissecting Co-Simulation parameters')
        self.__parameters_xml_manager = \
            common.parameters_xml_manager.ParametersXmlManager(configuration_manager=self.__configuration_manager,
                                                               logger=self.__logger,
                                                               xml_filename=self.__args.parameters)

        # STEP 5.1 - Dissecting Co-Simulation Parameters XML file
        if not self.__parameters_xml_manager.dissect() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.CoSimulatorReturnCodes.XML_ERROR

        # STEP 5.2 - Getting the variables found in the Co-Simulation Parameters file
        self.__parameters_variables_dict = self.__parameters_xml_manager.get_variables_dict()

        # STEP 5.3 - Getting the parameters found in the Co-Simulation Parameters file
        self.__parameters_parameters_dict = self.__parameters_xml_manager.get_parameters_dict()

        # STEP 5.4 - Getting the Co-Simulation parameters to be dump into a json file
        self.__parameters_parameters_for_json_file_dict = self.__parameters_xml_manager.get_parameter_for_json_dict()

        self.__logger.info('Co-Simulation parameters loaded from {}'.format(self.__args.parameters))
        self.__logger.info('Co-Simulator STEP 5 done')

        ########
        # STEP 6 - Co-Simulation Actions (processing the XML configuration files)
        ########
        self.__logger.info('Co-Simulator STEP 6, dissecting Co-Simulation Actions XML files')
        # STEP 6.1 - Getting the Actions Popen arguments, the CO_SIM_ variables transformation is performed 
        self.__actions_xml_manager = \
            common.actions_xml_manager.ActionsXmlManager(configuration_manager=self.__configuration_manager,
                                                         logger=self.__logger,
                                                         variables_manager=self.__variables_manager,
                                                         action_plan=self.__action_plan_dict)
        if not self.__actions_xml_manager.dissect() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.CoSimulatorReturnCodes.XML_ERROR

        self.__actions_popen_args_dict = self.__actions_xml_manager.get_actions_popen_arguments_dict()
        self.__logger.info('Co-Simulator STEP 6 done')

        ########
        # STEP 7 - Arranging run time environment
        ########
        self.__logger.info('Co-Simulator STEP 7, arranging environment')
        self.__items_to_be_arranged = self.__plan_xml_manager.get_items_to_be_arranged_dict()

        self.__arranger = common.arranger.Arranger(configuration_manager=self.__configuration_manager,
                                                   logger=self.__logger,
                                                   variables_manager=self.__variables_manager,
                                                   items_to_be_arranged_dict=self.__items_to_be_arranged)

        if not self.__arranger.arrange() == common.enums.ArrangerReturnCodes.OK:
            return common.enums.CoSimulatorReturnCodes.ARRANGER_ERROR
        self.__logger.info('Co-Simulator STEP 7 done')

        ########
        # STEP 8 - Converting Co-Simulation parameters from XML into JSON
        ########
        self.__logger.info('Co-Simulator STEP 8, transforming Co-Simulation parameters')
        if not self.generate_parameters_json_file() == common.enums.CoSimulatorReturnCodes.OK:
            return common.enums.CoSimulatorReturnCodes.JSON_FILE_ERROR
        self.__logger.info('Co-Simulator STEP 8 done')

        ########
        # STEP 9 - Launching the Action Plan
        ########
        self.__logger.info('Co-Simulator STEP 9, carrying out the Co-Simulation Action Plan Strategy')
        # self.__launcher = common.Launcher(action_plan_dict=self.__action_plan_dict,
        #                                   actions_popen_args_dict=self.__actions_popen_args_dict,
        #                                   configuration_manager=self.__configuration_manager,
        #                                   logger=self.__logger,
        #                                   log_Settings=self.__logger_settings)
        launching_manager = LaunchingManager(self.__action_plan_dict,
                                          self.__actions_popen_args_dict,
                                          self.__logger_settings,
                                          self.__configuration_manager)
        if not launching_manager.carry_out_action_plan() == common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.error('Error(s) were reported, check the errors log on {}'.format(
                self.__variables_manager.get_value(common.variables.CO_SIM_RESULTS_DIR)))
            return common.enums.CoSimulatorReturnCodes.LAUNCHER_ERROR
        # if not self.__launcher.carry_out_action_plan() == common.enums.LauncherReturnCodes.LAUNCHER_OK:
        #     self.__logger.error('Error(s) were reported, check the errors log on {}'.format(
        #         self.__variables_manager.get_value(common.variables.CO_SIM_RESULTS_DIR)))
        #     return common.enums.CoSimulatorReturnCodes.LAUNCHER_ERROR
        self.__logger.info('Co-Simulator STEP 8 done')

        ########
        # STEP 10 - Finishing
        ########
        self.__logger.info('Information about Co-Simulation process could be found on: {}'.format(
            self.__variables_manager.get_value(common.variables.CO_SIM_RESULTS_DIR)))
        self.__logger.info('END: Co-Simulation Co-Simulator')

        return common.enums.CoSimulatorReturnCodes.OK
