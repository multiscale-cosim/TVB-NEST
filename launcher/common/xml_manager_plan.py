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
import xml

# Co-Simulator's imports
import common


class XmlManagerPlan(common.XmlManager):
    """
        XML Manager for the Action Plan XML file
    """
    __action_plan_dict = {}

    def initialize_xml_elements(self):
        self._component_xml_tag = common.xml_tags.CO_SIM_XML_PLAN_ROOT_TAG

    def load_xml_into_dict(self):
        """
            Load the Co-Simulation plan XML file into __co_sim_plan_whole_xml_dict

        :return:
            XML_FORMAT_ERROR: The Co-Simulation Plan XML file is not well-formed
            XML_OK: The Co-Simulation Plan XML file has been loaded into _whole_xml_dict
        """
        try:
            self._whole_xml_dict = self._configuration_manager.get_configuration_settings(
                configuration_file=self._xml_filename,
                component=self._component_xml_tag)
        except xml.etree.ElementTree.ParseError:
            self._logger.error('{} cannot be loaded, check XML format'.format(self._xml_filename))
            return common.enums.XmlManagerReturnCodes.XML_FORMAT_ERROR
        except LookupError:
            self._logger.error(
                '{} cannot be loaded, {} tag not found'.format(self._xml_filename, self._component_xml_tag))
            return common.enums.XmlManagerReturnCodes.XML_FORMAT_ERROR
        else:
            self._logger.info('{} Co-Simulation Plan XML file loaded'.format(self._xml_filename))

        return common.enums.XmlManagerReturnCodes.XML_OK

    def __build_action_plan_dict_from_whole_dict(self):
        """
            Takes the whole dictionary representing the XML action plan file,
            and extract the content from the <action_plan> section

        :return:

            XML_OK: the action plan dictionary was built properly
        """
        xml_action_plan_dict = {}

        try:
            xml_action_plan_dict = self._main_xml_sections_dicts_dict['action_plan']
        except KeyError:
            self._logger.error('{} has no <action_plan>...</action_plan> section'.format(self._xml_filename))
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        # processing the dictionary gathered from the XML configuration file
        # on a sorted way, just following the correlative order of the name
        # of each action. <action_NNN> where NNN = indicates a correlative number
        for key, value in sorted(xml_action_plan_dict.items()):
            # getting the action type, i.e. CO_SIM_ACTION_SCRIPT, CO_SIM_EVENT
            try:
                action_type = value['action_type']
            except KeyError:
                self._logger.error('{} contains {} with no <action_type> tag'.format(self._xml_filename, key))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # Verifying whether the <action_type> element has the proper CO_SIM_ constant value or not
            if action_type not in common.constants.CO_SIM_ACTION_TYPES_TUPLE:
                self._logger.error(
                    '{} has <{}><action_type> a wrong value {}'.format(self._xml_filename, key, action_type))
                return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR

            # TO BE DONE: Checking the content of <action_launch_method> and <action_event>

            # Filling up the action plan dictionary
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
        self.__action_plan_dict = {}

        return self.__build_action_plan_dict_from_whole_dict()

    def get_action_plan_dict(self):
        """
            Getter of the attribute __action_plan_dict

        :return:
                __action_plan_dict attribute
        """
        return self.__action_plan_dict




