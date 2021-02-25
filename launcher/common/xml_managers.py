import common
import xml


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

    def build_parameters_dict_from_xml_main_dicts(self):
        """
            Builds a dictionary based on the <parameters> section of the processing XML file
            and the values will be gathered from the run-time environment parameters or parameters

        :return:
            XML_TAG_ERROR - The 'parameters' tag was not found in the processing XML file
            XML_OK - The parameters from the XML file were processed properly
        """
        self._parameters_dict = {}

        try:
            xml_parameters_dict = self._main_xml_sections_dicts_dict['parameters']
        except KeyError:
            self._logger.error('{} has no <parameters>...</parameters> section'.format(self._xml_filename))
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        #if not xml_parameters_dict:


        for key, value in xml_parameters_dict.items():
            # key is the XML tag parameter name, e.g. par_000 value is a dictionary defining the parameter,
            # e.g {'par_name': 'CO_SIM_EXECUTION_ENVIRONMENT', 'par_value': 'Cluster'} 

            # getting the parameter name
            try:
                parameter_name = value['par_name']
            except KeyError:
                self._logger.error('{} contains {} with no <par_name> tag'.format(self._xml_filename, key))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # getting the parameter value
            try:
                parameter_value = value['par_value']
            except KeyError:
                self._logger.error('{} contains {} with no <par_value> tag'.format(self._xml_filename, key))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            self._parameters_dict[parameter_name] = parameter_value

        return common.enums.XmlManagerReturnCodes.XML_OK

    def build_variables_dict_from_xml_main_dicts(self):
        """
            Builds a dictionary based on the <variables> section of the processing XML file
            and the values will be gathered from the run-time environment variables or parameters
        :return:
            XML_TAG_ERROR - The 'variables' tag was not found in the processing XML file
            XML_OK - The variables from the XML file were processed properly
        """
        self._variables_dict = {}

        try:
            xml_variables_dict = self._main_xml_sections_dicts_dict['variables']
        except KeyError:
            self._logger.error('{} has no <variables>...</variables> section'.format(self._xml_filename))
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        if not xml_variables_dict:
            self._logger.info('{} does not contains defined co-simulation variables')
            return common.enums.XmlManagerReturnCodes.XML_OK

        for key, value in xml_variables_dict.items():
            # key is the XML tag variable name, e.g. par_000
            # value is a dictionary defining the variable, e.g {'par_name': 'CO_SIM_DELAY', 'par_value': '100'}

            # getting the variable name
            try:
                variable_name = value['var_name']
            except KeyError:
                self._logger.error('{} contains {} with no <var_name> tag'.format(self._xml_filename, key))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            # getting the variable value
            try:
                variable_value = value['var_value']
            except KeyError:
                self._logger.error('{} contains {} with no <var_value> tag'.format(self._xml_filename, key))
                return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

            self._variables_dict[variable_name] = variable_value

        return common.enums.XmlManagerReturnCodes.XML_OK

    def dissect(self):
        """

        :return:
        """
        # Setting up the XML tags particularly used by XML Manager the sub-class
        self.initialize_xml_elements()

        # loading XML into a dict
        if not self.load_xml_into_dict() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_FORMAT_ERROR

        # splitting the whole dict into different dicts based on main tags
        if not self.split_whole_xml_dict_into_dict_by_sections() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR

        # In this point, _main_xml_sections_dicts_dict dictionary contains the dictionaries based on the
        # main expected tags on the Co-Simulation Plan XML configuration file,
        # hence, the _whole_xml_dict is deleted
        del self._whole_xml_dict

        # creating the parameters dict by getting the elements defined in the XML file parameters section
        if not self.build_parameters_dict_from_xml_main_dicts() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR

        # creating the variables dict by gathering the elements defined in the XML file variables section
        if not self.build_variables_dict_from_xml_main_dicts() == common.enums.XmlManagerReturnCodes.XML_OK:
            return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR

        return common.enums.XmlManagerReturnCodes.XML_OK

    def get_parameters_dict(self):
        """
        :return: _co_sim_parameters_dict
                    Dictionary containing the CO_SIM_* parameters created based on the
                    Co-Simulation XML configuration file (plan, parameters)

        """
        return self._parameters_dict

    def get_variables_dict(self):
        """
        :return: _co_sim_variables_dict
                    Dictionary containing the CO_SIM_* variables created based on the
                    Co-Simulation XML configuration file (plan, parameters)

        """
        return self._variables_dict


class CoSimulationPlanXmlManager(XmlManager):
    def initialize_xml_elements(self):
        # TO BE DONE: there should be a global XML file where tags are defined
        self._component_xml_tag = 'co_simulation_action_plan'

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

    # def build_parameters_dict_from_xml_main_dicts(self):
    #     """
    #         Validating the values set on the Co-Simulation Plan XML file
    #
    #     :return:
    #         XML_VALUE_ERROR: The Co-Simulation Plan XML file contains a wrong value
    #         XML_OK: All the found values are valid
    #     """
    #     # Execution Environment
    #     try:
    #         tmp_exec_env = self._main_xml_sections_dicts_dict['parameters']['execution_environment']
    #     except KeyError:
    #         self._logger.error('{} has no <execution_environment> tag in <plan_parameters>'.format(self._xml_filename))
    #         return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR
    #
    #     if 'LOCAL' == tmp_exec_env.upper():
    #         self._parameters_dict['execution_environment'] = 'LOCAL'
    #     elif 'CLUSTER' == tmp_exec_env.upper():
    #         self._parameters_dict['execution_environment'] = 'CLUSTER'
    #     else:
    #         self._logger.error('{} has {} for the <execution_environment> tag'.format(self._xml_filename, tmp_exec_env))
    #         return common.enums.XmlManagerReturnCodes.XML_VALUE_ERROR
    #
    #     return common.enums.XmlManagerReturnCodes.XML_OK

    # """
    # def build_variables_dict_from_xml_main_dicts(self):
    #     """
    #
    #     :return:
    #         XML_OK parameters
    #     """
    #     # TO BE DONE: parse the defined variables from the passed XML file
    #     self._variables_dict['__TO_BE_DONE__'] = {'parse': 'variables from XML'}
    #     return common.enums.XmlManagerReturnCodes.XML_OK
    #     """


class CoSimulationParametersXmlManager(XmlManager):
    def initialize_xml_elements(self):
        # TO BE DONE: there should be a global XML file where tags are defined
        self._component_xml_tag = 'co_simulation_parameters'

    def load_xml_into_dict(self):
        """
            Load the Co-Simulation parameters XML file into __co_sim_parameters_whole_xml_dict

        :return:
            CO_SIM_parameters_XML_FORMAT_ERROR: The Co-Simulation parameters XML file is not well-formed
            CO_SIM_parameters_XML_OK: The Co-Simulation parameters XML file has been loaded into _whole_xml_dict
        """
        try:
            self._whole_xml_dict = self._configuration_manager.get_configuration_settings(
                configuration_file=self._xml_filename,
                component='co_simulation_parameters')
        except xml.etree.ElementTree.ParseError:
            self._logger.error('{} cannot be loaded, check XML format'.format(self._xml_filename))
            return common.enums.XmlManagerReturnCodes.XML_FORMAT_ERROR
        else:
            self._logger.info('{} Co-Simulation parameters XML file loaded'.format(self._xml_filename))

        return common.enums.XmlManagerReturnCodes.XML_OK

    # def build_parameters_dict_from_xml_main_dicts(self):
    #     """
    #         Validating the values set on the Co-Simulation parameters XML file
    #
    #     :return:
    #         XML_VALUE_ERROR: The Co-Simulation parameters XML file contains a wrong value
    #         XML_OK: All the found values are valid
    #     """
    #     # getting elements to generate the /path/to/results/parameters.json file
    #     try:
    #         tmp_parameters_from_xml = self._main_xml_sections_dicts_dict['parameters']['param_TR_nest_to_tvb']
    #     except KeyError:
    #         self._logger.error('{} has no <param_TR_nest_to_tvb> tag in <parameters>'.format(self._xml_filename))
    #         return common.enums.XmlManagerReturnCodes.XML_TAG_ERROR
    #
    #     self._parameters_dict['param_TR_nest_to_tvb'] = tmp_parameters_from_xml
    #     return common.enums.XmlManagerReturnCodes.XML_OK
# """
#     def build_variables_dict_from_xml_main_dicts(self):
#         """
#             Empty method since variables declaration is not expected on the parameters XML file
#
#         :return:
#             XML_OK just to let the super-class to continue the normal logical flow
#         """
#         return common.enums.XmlManagerReturnCodes.XML_OK
# """
