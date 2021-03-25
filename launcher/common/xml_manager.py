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

# Co-Simulator imports
import common


class XmlManager(object):
    """
        Template for XML managers
    """

    # general members
    _configuration_manager = None
    _logger = None
    _xml_filename = None

    # expected members from sub-classes
    _component_xml_tag = ''  # e.g. co_simulation_action_plan, co_simulation_parameters
    _xml_main_tags = set()

    # dictionaries
    _main_xml_sections_dicts_dict = {}
    _parameters_dict = {}
    _variables_dict = {}
    _whole_xml_dict = {}

    def __init__(self, configuration_manager=None, logger=None, xml_filename=None):
        # getting objects referenced provided when the instance object is created
        self._configuration_manager = configuration_manager
        self._logger = logger
        self._xml_filename = xml_filename

        # attributes to be set on sub-classes
        self._component_xml_tag = ''
        self._xml_main_tags = set()

        # dictionaries
        self._main_xml_sections_dicts_dict = {}
        self._parameters_dict = {}
        self._variables_dict = {}
        self._whole_xml_dict = {}

    def initialize_xml_elements(self):
        # proper initialization must be implemented in the sub-class
        self._logger.debug('invoking initialize_xml_elements from XmlManager super class')
        return common.enums.XmlManagerReturnCodes.XML_WRONG_MANAGER_ERROR

    def load_xml_into_dict(self):
        # proper loading procedure must be implemented in the sub-class
        self._logger.debug('invoking load_xml_into_dict from XmlManager super class')
        return common.enums.XmlManagerReturnCodes.XML_WRONG_MANAGER_ERROR

    def split_whole_xml_dict_into_dict_by_sections(self):
        """
            Creates a dictionary of dictionaries based on the main elements
            of the XML file under processing

        :return:
            XML_OK: The dictionary of dictionaries has been successfully created.
        """

        for xml_main_tag in self._whole_xml_dict:
            self._main_xml_sections_dicts_dict[xml_main_tag] = self._whole_xml_dict[xml_main_tag]

        return common.enums.XmlManagerReturnCodes.XML_OK

    def _build_variables_dict_from_xml_main_dicts(self):
        """
            Builds a dictionary based on the <variables> section of the processing XML file
            and the values will be gathered from the run-time environment variables or parameters

        :return:
            XML_TAG_ERROR - The 'variables' tag was not found in the processing XML file
            XML_OK - The variables from the XML file were processed properly
        """
        self._variables_dict = {}

        try:
            xml_variables_dict = self._main_xml_sections_dicts_dict[common.xml_tags.CO_SIM_XML_VARIABLES]
        except KeyError:
            self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                       common.xml_tags.CO_SIM_XML_VARIABLES,
                                                                       common.xml_tags.CO_SIM_XML_VARIABLES))
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        if not xml_variables_dict:
            self._logger.info('{} does not contains defined co-simulation variables')
            return common.enums.XmlManagerReturnCodes.XML_OK

        for key, value in xml_variables_dict.items():
            # key   -> XML tag referring to the variable name, e.g. var_000
            # value -> Dictionary defining the variable, e.g.
            # {'var_name': 'CO_SIM_EXECUTION_ENVIRONMENT', 'var_value': 'Cluster'}

            # getting the variable name
            try:
                variable_name = value[common.xml_tags.CO_SIM_XML_VARIABLE_NAME]
            except KeyError:
                self._logger.error('{} contains {} with no <{}> tag'.format(self._xml_filename,
                                                                            key,
                                                                            common.xml_tags.CO_SIM_XML_VARIABLE_NAME))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # getting the variable value
            # NOTE: The value could contain reference to environment variables, e.g. ${ENV_VAR}
            #       or Co-Simulator variables, e.g. CO_SIM_*
            #       They will be transformed into values
            try:
                variable_value = value[common.xml_tags.CO_SIM_XML_VARIABLE_VALUE]
            except KeyError:
                self._logger.error('{} contains {} with no <{}> tag'.format(self._xml_filename,
                                                                            key,
                                                                            common.xml_tags.CO_SIM_XML_VARIABLE_VALUE))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            self._variables_dict[variable_name] = variable_value

        return common.enums.XmlManagerReturnCodes.XML_OK

    def _build_parameters_dict_from_xml_main_dicts(self):
        """
            Builds a dictionary based on the <parameters> section of the processing XML file
            and the values will be gathered from the run-time environment parameters or parameters

        :return:
            XML_TAG_ERROR - The 'parameters' tag was not found in the processing XML file
            XML_OK - The parameters from the XML file were processed properly
        """
        self._parameters_dict = {}

        try:
            xml_parameters_dict = self._main_xml_sections_dicts_dict[common.xml_tags.CO_SIM_XML_PARAMETERS]
        except KeyError:
            self._logger.error('{} has no <{}>...</{}> section'.format(self._xml_filename,
                                                                       common.xml_tags.CO_SIM_XML_PARAMETERS,
                                                                       common.xml_tags.CO_SIM_XML_PARAMETERS))
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        # In this point, xml_parameters_dict must content the representation of the XML parameters sections,
        # meaning that at least one parameter element is expected even though this is a mock one

        for key, value in xml_parameters_dict.items():
            # key   -> The XML tag refering to the parameter name, e.g. par_000
            # value -> The dictionary defining the parameter per se, e.g.
            #           {'par_name': 'CO_SIM_DELAY', 'par_value': 100 }

            # getting the parameter name
            try:
                parameter_name = value[common.xml_tags.CO_SIM_XML_PARAMETER_NAME]
            except KeyError:
                self._logger.error('{} contains {} with no <{}> tag'.format(self._xml_filename,
                                                                            key,
                                                                            common.xml_tags.CO_SIM_XML_PARAMETER_NAME))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # getting the parameter value
            try:
                parameter_value = value[common.xml_tags.CO_SIM_XML_PARAMETER_VALUE]
            except KeyError:
                self._logger.error('{} contains {} with no <{}> tag'.format(self._xml_filename,
                                                                            key,
                                                                            common.xml_tags.CO_SIM_XML_PARAMETER_VALUE))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            self._parameters_dict[parameter_name] = parameter_value

        return common.enums.XmlManagerReturnCodes.XML_OK

    def build_particular_sections_dicts(self):
        """
            Abstract method called at the end of the dissect method, just to give the chance
            of sub-classes to gather additional section from the Co-Simulation XML file

        :return:
            XML_OK - Just to by pass the checking when the method is not defined on the sub-class
        """

        return common.enums.XmlManagerReturnCodes.XML_OK

    def __transform_environment_variables_into_values(self, input_dictionary=None):
        """
            Transforms the referenced variables names into its values based
            on CO_SIM_* variables or environment variables.

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
            XML_ENVIRONMENT_VARIABLE_ERROR: The value for a referenced variable could not been obtained
        """
        for key, value in input_dictionary.items():
            # variable_name = key
            functional_variable_value = value

            try:
                runtime_variable_value = common.utils.transform_environment_variables_into_values(
                    functional_variable_value=functional_variable_value)
                # replacing the run-time value of the variable after having been transformed
                input_dictionary[key] = runtime_variable_value
            except common.exceptions.EnvironmentVariableNotSet as EnvironmentVariableNotSet:
                self._logger.error(EnvironmentVariableNotSet)
                return common.enums.XmlManagerReturnCodes.XML_ENVIRONMENT_VARIABLE_ERROR

        return common.enums.XmlManagerReturnCodes.XML_OK

    def dissect(self):
        """
            Gather the variables parameters from the whole XML dictionary
            and populate the _parameter_dict and _variables_dict attributes respectively
            e.g.
            _variables_dict = {'CO_SIM_XML_ACTIONS_DIR': '${CO_SIM_TVB_NEST}/launcher/actions',
                                'CO_SIM_EXECUTION_ENVIRONMENT': 'Local'}

            _parameters_dict = { 'CO_SIM_DELAY': '100',
                                'CO_SIM_RESULTS_DIR': 'CO_SIM_RUNTIME_RESULTS_DIR',
                                'CO_SIM_INPUT_FILE': 'input/0.txt',
                                'CO_SIM_OUTPUT_FILE': 'output/0.txt'}
        :return:
            XML_FORMAT_ERROR
            XML_TAG_ERROR
            XML_VALUE_ERROR
            XML_ENVIRONMENT_VARIABLE_ERROR
            XML_OK
        """
        # Setting up the XML tags particularly used by XML Manager the sub-class
        self.initialize_xml_elements()

        # Step 1 - Loading XML into a _whole_xml_dict attribute
        if not self.load_xml_into_dict() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_FORMAT_ERROR

        # Step 2 - Splitting the whole dict into different dicts based on main tags, e.g. variables, parameters, etc
        if not self.split_whole_xml_dict_into_dict_by_sections() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        # In this point, _main_xml_sections_dicts_dict dictionary contains the dictionaries based on the
        # main expected tags on the Co-Simulation Plan XML configuration file,
        # hence, the _whole_xml_dict could be deleted
        del self._whole_xml_dict

        # Step 3 - Variables
        # Step 3.1  - Creating the variables dict by gathering the elements defined in the XML file variables section
        if not self._build_variables_dict_from_xml_main_dicts() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR

        # Step 3.2 - Transforming environment variables references into run-time values
        if not self.__transform_environment_variables_into_values(input_dictionary=self._variables_dict) == \
               common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_ENVIRONMENT_VARIABLE_ERROR

        # Step 4 - Parameters
        # Step 4.1  -   Creating the parameters dict by getting the elements
        #               defined in the XML file parameters section
        if not self._build_parameters_dict_from_xml_main_dicts() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR

        # Step 99 - Calling the ending method for managing the particular XML sections,
        #           if it is defined in the sub-class, otherwise the abstract method will be called.
        if not self.build_particular_sections_dicts() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR

        return common.enums.XmlManagerReturnCodes.XML_OK

    def get_parameters_dict(self):
        """
            Getter of the dictionary containing the Co-Simulation parameters loaded from the XML file

        :return: _co_sim_parameters_dict
                    Dictionary containing the CO_SIM_* parameters created based on the
                    Co-Simulation XML configuration file (plan, parameters)

        """
        return self._parameters_dict

    def get_variables_dict(self):
        """
            Getter of the dictionary containing the Co-Simulation variables loaded from the XML file

        :return: _co_sim_variables_dict
                    Dictionary containing the CO_SIM_* variables created based on the
                    Co-Simulation XML configuration file (plan, parameters)

        """
        return self._variables_dict


