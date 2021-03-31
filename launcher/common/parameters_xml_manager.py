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

# Co-Simulator's import
import common


class ParametersXmlManager(common.XmlManager):
    """
        XML Manager for the Parameters XML file
    """

    def initialize_xml_elements(self):
        # TO BE DONE: there should be a global XML file where tags are defined
        self._component_xml_tag = 'co_simulation_parameters'

    # def load_xml_into_dict(self):
    #     """
    #         Load the Co-Simulation parameters XML file into _whole_xml_dict
    #
    #     :return:
    #         CO_SIM_parameters_XML_FORMAT_ERROR: The Co-Simulation parameters XML file is not well-formed
    #         CO_SIM_parameters_XML_OK: The Co-Simulation parameters XML file has been loaded into _whole_xml_dict
    #     """
    #     try:
    #         self._whole_xml_dict = self._configuration_manager.get_configuration_settings(
    #             configuration_file=self._xml_filename,
    #             component=self._component_xml_tag)
    #     except xml.etree.ElementTree.ParseError:
    #         self._logger.error('{} cannot be loaded, check XML format'.format(self._xml_filename))
    #         return common.enums.XmlManagerReturnCodes.XML_FORMAT_ERROR
    #     else:
    #         self._logger.info('{} Co-Simulation parameters XML file loaded'.format(self._xml_filename))
    #
    #     return common.enums.XmlManagerReturnCodes.XML_OK
