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
# Co-Simulator's imports
import common


class PlanXmlManager(common.XmlManager):
    """
        XML Manager for the Action Plan XML file
    """
    __action_plan_dict = {}
    __items_to_be_arranged = {}

    def initialize_xml_elements(self):
        self._component_xml_tag = common.xml_tags.CO_SIM_XML_PLAN_ROOT_TAG

    def __build_items_to_be_arranged_dict_from_whole_dict(self):
        """
            Takes the whole dictionary representing the Action Plan XML file
            and extracts the content from the <arrange> section
        :return:
            XML_OK:
        """

        self.__items_to_be_arranged = {}

        try:
            items_to_be_arranged_dict = self._main_xml_sections_dicts_dict[common.xml_tags.CO_SIM_XML_PLAN_ARRANGEMENT]
        except KeyError:
            self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                       common.xml_tags.CO_SIM_XML_PLAN_ARRANGEMENT,
                                                                       common.xml_tags.CO_SIM_XML_PLAN_ARRANGEMENT))
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        for key, value in sorted(items_to_be_arranged_dict.items()):
            # key = arrangement XML id, e.g. arr_001
            arrangement_duty = value[common.xml_tags.CO_SIM_XML_ARRANGEMENT_DUTY]

            # Verifying whether the <action_type> element has the proper CO_SIM_ constant value or not
            if arrangement_duty not in common.constants.CO_SIM_ARRANGEMENT_DUTIES_TUPLE:
                self._logger.error(
                    '{} has <{}><{}> a wrong value {}'.format(self._xml_filename,
                                                              key,
                                                              common.xml_tags.CO_SIM_XML_ARRANGEMENT_DUTY,
                                                              arrangement_duty))
                return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR

            # e.g.
            # items_to_be_arranged['arr_001']
            # {'arr_what': '{CO_SIM_RESULTS_DIR}/{CO_SIM_RESULTS_INPUT_DIR}',
            #  'arr_operation': 'CO_SIM_ARRANGEMENT_DIR_CREATION'}
            self.__items_to_be_arranged[key] = value

        return common.enums.XmlManagerReturnCodes.XML_OK

    def __build_action_plan_dict_from_whole_dict(self):
        """
            Takes the whole dictionary representing the XML action plan file,
            and extracts the content from the <action_plan> section

        :return:

            XML_OK: the action plan dictionary was built properly
        """
        xml_action_plan_dict = {}

        try:
            xml_action_plan_dict = self._main_xml_sections_dicts_dict[common.xml_tags.CO_SIM_XML_PLAN_ACTION_PLAN]
        except KeyError:
            self._logger.error('{} has no <{}}>...</{}}> section'.format(self._xml_filename,
                                                                         common.xml_tags.CO_SIM_XML_PLAN_ACTION_PLAN,
                                                                         common.xml_tags.CO_SIM_XML_PLAN_ACTION_PLAN))
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        # processing the dictionary gathered from the XML configuration file
        # on a sorted way, just following the correlative order of the name
        # of each action. <action_NNN> where NNN = indicates a correlative number
        for key, value in sorted(xml_action_plan_dict.items()):
            # getting the action type, i.e. CO_SIM_ACTION_SCRIPT, CO_SIM_EVENT
            try:
                action_type = value[common.xml_tags.CO_SIM_XML_PLAN_ACTION_TYPE]
            except KeyError:
                self._logger.error('{} contains {} with no <{}> tag'.format(self._xml_filename, key,
                                                                            common.xml_tags.CO_SIM_XML_PLAN_ACTION_TYPE))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # Verifying whether the <action_type> element has the proper CO_SIM_ constant value or not
            if action_type not in common.constants.CO_SIM_ACTION_TYPES_TUPLE:
                self._logger.error(
                    '{} has <{}><{}> a wrong value {}'.format(self._xml_filename, key,
                                                               common.xml_tags.CO_SIM_XML_PLAN_ACTION_TYPE,
                                                               action_type))
                return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR

            # TO BE DONE: Checking the content of <action_launch_method> and <action_event> against *_TUPLE

            # Filling up the action plan dictionary
            # e.g.
            # action_plan_dict['action_000'] =
            # {'action_type': 'CO_SIM_ACTION',
            #  'action_xml': 'initial_spikes_generator.xml',
            #  'action_launch_method': 'CO_SIM_SEQUENTIAL_ACTION'}
            self.__action_plan_dict[key] = value

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

        self.__items_to_be_arranged = {}
        items_to_be_arranged_return = self.__build_items_to_be_arranged_dict_from_whole_dict()
        if not items_to_be_arranged_return == common.enums.XmlManagerReturnCodes.XML_OK:
            return items_to_be_arranged_return

        self.__action_plan_dict = {}
        action_plan_builder_return = self.__build_action_plan_dict_from_whole_dict()
        if not action_plan_builder_return == common.enums.XmlManagerReturnCodes.XML_OK:
            return action_plan_builder_return

        return common.enums.XmlManagerReturnCodes.XML_OK

    def get_items_to_be_arranged_dict(self):
        """
            Getter of the __items_to_be_arranged_dict attribute
        :return:
            __items_to_be_arranged_dict

        """
        return self.__items_to_be_arranged

    def get_action_plan_dict(self):
        """
            Getter of the __action_plan_dict attribute

        :return:
                __action_plan_dict attribute
        """
        return self.__action_plan_dict




