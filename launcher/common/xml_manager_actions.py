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

# Co-Simulator's imports
import common


class XmlManagerActions(object):
    """
        XML Manager for the Co-Simulation Actions XML files

        NOTE: This class mimic the behaviour of the XmlManager,
                nevertheless, goes through the actions dictionary
                and each entry in the dictionary is processed
                with the XMLManager sub-class __CoSimulationActionXmlManager
    """
    __actions_popen_arguments_dict = {}

    def __init__(self, configuration_manager=None, logger=None, environment_variables_manager=None, action_plan=None):
        self.__configuration_manager = configuration_manager
        self.__logger = logger
        self.__variables_manager = environment_variables_manager
        self.__action_plan = action_plan

    def __transform_co_sim_variables_into_values(self, popen_arguments_list=None):
        """
            Goes through the elements in the Popen arguments list to find references to the CO_SIM_* variables,
            and transform them into the run time values

        :return:
            XML_OK: All the CO_SIM_* variables references were transformed into the corresponding run time values
        """
        for index, item in enumerate(popen_arguments_list):
            try:
                popen_arguments_list[index] = \
                    common.utils.transform_co_simulation_variables_into_values(variables_manager=self.__variables_manager,
                                                                               functional_variable_value=item)
            except KeyError:
                self.__logger.error('{} references to a CO_SIM_ variable not have been set yet'.format(item))
                return common.enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR

        # Removing those items with empty value, i.e. equal to ''
        if self.__variables_manager.get_value(variable_name=common.variables.CO_SIM_EMPTY) in popen_arguments_list:
            popen_arguments_list.remove(self.__variables_manager.get_value(variable_name=common.variables.CO_SIM_EMPTY))

        return common.enums.XmlManagerReturnCodes.XML_OK

    def dissect(self):
        """
            Takes each XML action file reference in the XML action plan configuration file
            and dissect them by using the nested Action XML Manager sub-class

        :return:
            XML_CO_SIM_VARIABLE_ERROR: At least a CO_SIM_* variable is not managed by the
            XML_OK: All actions XML files were processed correctly
        """
        actions_xml_file_location = \
            self.__variables_manager.get_value(common.variables.CO_SIM_ACTIONS_DIR)

        for key, value in self.__action_plan.items():
            # key = action_NNN <- the identification in the action plan
            if value[common.xml_tags.CO_SIM_XML_PLAN_ACTION_TYPE] == common.constants.CO_SIM_ACTION:
                # taking into account only actions (scripts or binaries) able to be executed

                current_action_id = key  # action_NNN
                current_action_xml_path_filename = os.sep.join([actions_xml_file_location,
                                                                value[common.xml_tags.CO_SIM_XML_PLAN_ACTION_XML],
                                                                ])

                xml_action_manager = self._CoSimulationActionXmlManager(
                    configuration_manager=self.__configuration_manager,
                    logger=self.__logger,
                    xml_filename=current_action_xml_path_filename)

                # split XML dictionary into dictionaries by XML section
                # at the end of the action XML dissection process
                # there will be an attribute (list) with the Popen arguments
                dissect_return = xml_action_manager.dissect()
                if not dissect_return == common.enums.XmlManagerReturnCodes.XML_OK:
                    self.__logger.error('Error found dissecting {}'.format(current_action_xml_path_filename))
                    return dissect_return

                # raw arguments values gathered from XML configuration file
                popen_arguments_list = xml_action_manager.get_Popen_arguments_list()

                # transform CO_SIM_* variables
                # NOTE: the CO_SIM_* variables must have the run-time values assigned in this point,
                # otherwise, the Co-Simulation process will not be performed properly
                if not self.__transform_co_sim_variables_into_values(popen_arguments_list=popen_arguments_list) == \
                       common.enums.XmlManagerReturnCodes.XML_OK:
                    self.__logger.error(
                        'Error found transforming into values the CO_SIM_ variables found in {}'.format(
                            current_action_xml_path_filename))
                    return common.enums.XmlManagerReturnCodes.XML_CO_SIM_VARIABLE_ERROR

                self.__actions_popen_arguments_dict[key] = popen_arguments_list

        return common.enums.XmlManagerReturnCodes.XML_OK

    def get_actions_popen_arguments_dict(self):
        """

        :return:
            Dictionary containing the popen argument list keyed by action identification in the action plan
        """
        return self.__actions_popen_arguments_dict

    class _CoSimulationActionXmlManager(common.XmlManager):
        """
            XML Manager for the Co-Simulation Actions XML files
        """

        __performer_dict = {}
        __Popen_arguments_list = []

        def initialize_xml_elements(self):
            # TO BE DONE: there should be a global XML file where tags are defined
            self._component_xml_tag = common.xml_tags.CO_SIM_XML_ACTION_ROOT_TAG

        def load_xml_into_dict(self):
            """
                Load a Co-Simulation Action XML file into _whole_xml_dict

            :return:
                CO_SIM_parameters_XML_FORMAT_ERROR: The Co-Simulation Action XML file is not well-formed
                CO_SIM_parameters_XML_OK: The Co-Simulation Action XML file has been loaded into _whole_xml_dict
            """
            try:
                self._whole_xml_dict = self._configuration_manager.get_configuration_settings(
                    configuration_file=self._xml_filename,
                    component=self._component_xml_tag)
            except xml.etree.ElementTree.ParseError:
                self._logger.error('{} cannot be loaded, check XML format'.format(self._xml_filename))
                return common.enums.XmlManagerReturnCodes.XML_FORMAT_ERROR
            else:
                self._logger.info('{} Co-Simulation action XML file loaded'.format(self._xml_filename))

            return common.enums.XmlManagerReturnCodes.XML_OK

        def __dissect_performer_section(self):
            """
                Fills the Popen list from the performer section
            :return:
                XML_TAG_ERROR: Error found dissecting the performer section of the action section
                XML_OK: The performer section was dumped properly into the Popen arguments list
            """
            # peformer bynary
            try:
                self.__Popen_arguments_list.append(
                    self.__performer_dict[common.xml_tags.CO_SIM_XML_ACTION_PERFORMER_BINARY])
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_PERFORMER_BINARY,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_PERFORMER_BINARY))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # arguments for the performer binary
            try:
                performer_arguments_dict = self.__performer_dict[common.xml_tags.CO_SIM_XML_ACTION_PERFORMER_ARGUMENTS]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_PERFORMER_ARGUMENTS,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_PERFORMER_ARGUMENTS))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            for key, value in performer_arguments_dict.items():
                # key = argv_NN -> Argument identification
                self.__Popen_arguments_list.append(value)

            return common.enums.XmlManagerReturnCodes.XML_OK

        def __dissect_routine_section(self):
            """
                Fills the Popen list from the routine section
            :return:
                XML_TAG_ERROR: Error found dissecting the routine section of the action section
                XML_OK: The routine section was dumped properly into the Popen arguments list
            """
            # peformer bynary
            try:
                self.__Popen_arguments_list.append(
                    self.__routine_dict[common.xml_tags.CO_SIM_XML_ACTION_ROUTINE_CODE])
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_ROUTINE_CODE,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_ROUTINE_CODE))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # arguments for the routine binary
            try:
                routine_arguments_dict = self.__routine_dict[common.xml_tags.CO_SIM_XML_ACTION_ROUTINE_ARGUMENTS]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_ROUTINE_ARGUMENTS,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_ROUTINE_ARGUMENTS))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            for key, value in routine_arguments_dict.items():
                # key = argv_NN -> Argument identification
                self.__Popen_arguments_list.append(value)

            return common.enums.XmlManagerReturnCodes.XML_OK

        def __build_Popen_arguments_list(self):
            """
                Takes the whole dictionary representing the whole action XML file,
                and extract the content from the <action> section

            :return:

                XML_OK: the Popen argument list was built properly
            """
            xml_action_dict = {}

            try:
                xml_action_dict = self._main_xml_sections_dicts_dict[common.xml_tags.CO_SIM_XML_ACTION]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           common.xml_tags.CO_SIM_XML_ACTION,
                                                                           common.xml_tags.CO_SIM_XML_ACTION))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # performer
            try:
                self.__performer_dict = xml_action_dict[common.xml_tags.CO_SIM_XML_ACTION_PERFORMER]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_PERFORMER,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_PERFORMER))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            if not self.__dissect_performer_section() == common.enums.XmlManagerReturnCodes.XML_OK:
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # routine
            try:
                self.__routine_dict = xml_action_dict[common.xml_tags.CO_SIM_XML_ACTION_ROUTINE]
            except KeyError:
                self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_ROUTINE,
                                                                           common.xml_tags.CO_SIM_XML_ACTION_ROUTINE))

            if not self.__dissect_routine_section() == common.enums.XmlManagerReturnCodes.XML_OK:
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            return common.enums.XmlManagerReturnCodes.XML_OK

        def build_particular_sections_dicts(self):
            """
                Implements the abstract method which is called at the end of the
                Co-Simulation XML file dissection process. In here it's a wrapper
                of the private method __build_action_plan_dict_from_whole_dict

            :return:
                The return code will be result provided by the private
                method __build_action_plan_dict_from_whole_dict,
                which could return the following results codes:

                XML_TAG_ERROR   -> The Co-Simulation XML file does not contain the expected TAGS
                                    related to the the action plan. e.g. <action_plan></action_plan>
                XML_VALUE_ERROR -> The Co-Simulation XML file does not contain the expected VALUES
                                    related to the action definition itself. e.g. CO_SIM_EVENT
                XML_OK:         -> The __action_plan_dict attributed has been filled properly
            """
            self.__Popen_arguments_list = []

            return self.__build_Popen_arguments_list()

        def get_Popen_arguments_list(self):
            return self.__Popen_arguments_list
