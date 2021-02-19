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
import common
import configurations_manager
import xml


class Launcher:
    """
        Class representing the co-simulation launcher tool

    Methods:
    --------
        run(args=None)
            Entry point to the launcher and executes the main loop of the tool
    """
    __args = None
    __co_sim_plan_xml_dict = None
    __configuration_manager = None
    __logger = None

    __xml_main_tags = ('plan_parameters', 'action_plan_variables', 'action_plan')
    __xml_main_dicts = {}  # will be created dynamically
    __action_plan_variables_dict = {}

    @property
    def __co_simulation_plan_xml_to_dict(self):
        """
            Load the Co-Simulation plan XML file into __co_sim_plan_xml_dict

        :return:
            CO_SIM_PLAN_XML_FORMAT_ERROR: The Co-Simulation Plan XML file is not well-formed
            CO_SIM_PLAN_XML_OK: The Co-Simulation Plan XML file has been loaded into __co_sim_plan_xml_dict
        """
        try:
            self.__co_sim_plan_xml_dict = self.__configuration_manager.get_configuration_settings(
                configuration_file=self.__args.plan,
                component='co_simulation_plan')
        except xml.etree.ElementTree.ParseError:
            self.__logger.error('{} cannot be loaded, check XML format'.format(self.__args.plan))
            return common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_FORMAT_ERROR
        else:
            self.__logger.info('{} Co-Simulation Plan XML file loaded'.format(self.__args.plan))

        return common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_OK

    def __co_sim_plan_xml_main_tags_to_dict(self):
        """
            Loading the Co-Simulation Plan XML file main sections into dictionaries

        :return:
            CO_SIM_PLAN_XML_TAG_ERROR:  When the Co-Simulation Plan XML file does not contains an expected tag
                                        on the first level
            CO_SIM_PLAN_XML_OK: Values present on the Co-Simulation Plan XML file are the expected ones.
        """

        for co_sim_plan_main_tag in self.__xml_main_tags:
            try:
                tmp_xml_dict = self.__co_sim_plan_xml_dict[co_sim_plan_main_tag]
            except KeyError:
                # Co-Simulation Plan XML File does not contains expected main tags
                self.__logger.error('{} does not contains the <{}> tag'.format(self.__args.plan, co_sim_plan_main_tag))
                return common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_TAG_ERROR

            self.__xml_main_dicts[co_sim_plan_main_tag] = tmp_xml_dict

        # a = self.__co_sim_plan_xml_dict['delay']

        # In this point, __xml_dict dictionary contains the dictionaries based on the
        # main expected tags on the Co-Simulation Plan XML configuration file,
        # hence, the __co_sim_plan_xml_dict is deleted
        del self.__co_sim_plan_xml_dict

        return common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_OK

    def __co_sim_plan_xml_check_plan_parameters(self):
        """
            Validating the values set on the Co-Simulation Plan XML file

        :return:
            CO_SIM_PLAN_XML_VALUE_ERROR: The Co-Simulation Plan XML file contains a wrong value
            CO_SIM_PLAN_XML_OK: All the found values are valid
        """
        # Execution Environment
        try:
            tmp_exec_env = self.__xml_main_dicts['plan_parameters']['execution_environment']
        except KeyError:
            self.__logger.error('{} has no <execution_environment> tag in <plan_parameters>'.format(self.__args.plan))
            return common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_TAG_ERROR

        if 'LOCAL' == tmp_exec_env.upper():
            self.__action_plan_variables_dict['__CO_SIM_EXECUTION_ENVIRONMENT'] = 'LOCAL'
        elif 'CLUSTER' == tmp_exec_env.upper():
            self.__action_plan_variables_dict['__CO_SIM_EXECUTION_ENVIRONMENT'] = 'CLUSTER'
        else:
            self.__logger.error('{} has {} for the <execution_environment> tag'.format(self.__args.plan, tmp_exec_env))
            return common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_VALUE_ERROR

        return common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_OK

    def run(self, args=None):
        """
            Entry point of the Co-Simulation Launcher tool

        :param args:
            There is no parameters to be used since argparse takes the sys.argv by default

        :return:
            common.enums.LauncherReturnCodes
        """

        # STEP 1 - Checking command line parameters
        try:
            self.__args = common.args.arg_parse()
        except SystemExit as e:
            # argument parser has reported some issue with the arguments
            return common.enums.LauncherReturnCodes.PARAMETER_ERROR

        # STEP 2 - Setting Up the Configuration Manager Configuration
        self.__configuration_manager = configurations_manager.ConfigurationsManager()
        self.__logger = self.__configuration_manager.load_log_configurations('launcher')
        self.__logger.info('START: Co-Simulation Launcher')

        # STEP 3 - Loading Co-Simulation Plan XML configuration file
        if self.__co_simulation_plan_xml_to_dict == common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_FORMAT_ERROR:
            return common.enums.LauncherReturnCodes.XML_ERROR

        # STEP 4 - Validating values on the Co-Simulation Plan XML configuration file
        # STEP 4.1 - Main Tags
        if self.__co_sim_plan_xml_main_tags_to_dict() == common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_TAG_ERROR:
            return common.enums.LauncherReturnCodes.XML_ERROR

        # STEP 4.2 - Plan parameters
        if self.__co_sim_plan_xml_check_plan_parameters() == common.enums.CoSimPlanXmlReturnCodes.CO_SIM_PLAN_XML_VALUE_ERROR:
            return common.enums.LauncherReturnCodes.XML_ERROR

        # STEP 5 - Launching action plan
        # TO BE DONE

        # STEP 99 - Finishing
        self.__logger.info('END: Co-Simulation Launcher')

        return common.enums.LauncherReturnCodes.OK
