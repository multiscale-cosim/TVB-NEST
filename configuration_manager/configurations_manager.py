# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements; and to You under the Apache License,
#  Version 2.0."

from definitions import CONFIG_FILE
from xml_parser import Parser
from config_logger import ConfigLogger
from directories_manager import DirectoriesManager


class ConfigurationsManager:
    """Manages all the configuration settings.

     Examples:
    >>> config_manager = ConfigurationsManager()


    # make a directory
    >>> config_manager.make_directory('test_directory') # doctest: +ELLIPSIS
    ...\\test_directory
    
    # load specified component settings as a dictionary object from XML configuration file
    >>> launcher_settings = config_manager.get_configuration_settings('launcher_configurations', CONFIG_FILE)
    >>> print(launcher_settings)
    {'foo': {'bar': None}, 'test_type': 'cluster'}

    >>> print(type(launcher_settings))
    <class 'dict'>

    # configure and load logger
    >>> myLogger = ConfigurationsManager().load_log_configurations(__name__)
    >>> myLogger.info("configured") # doctest: +ELLIPSIS
    20...INFO configurationsmanager... configured
    """

    __directories_manager = DirectoriesManager()
    __parser = Parser()
    __configuration_file = CONFIG_FILE

    def make_directory(self, directory):
        """Wrapper for making directories"""
        return self.__directories_manager.make_directory(directory)

    def get_directory(self, directory):
        """Wrapper for retrieving directories"""
        return self.__directories_manager.get_directory(directory)

    def load_xml(self, configuration_file, component):
        """Wrapper for loading an xml file"""
        # loads the xml configuration file as an xml.etree.ElementTree
        global_configurations_xml_tree = self.__parser.load_xml(configuration_file)
        root = global_configurations_xml_tree.getroot()
        # get the xml configuration settings for the desired component
        component_configurations_xml = root.find(component)
        if component_configurations_xml is None:
            # TODO: a better exception handling
            raise LookupError("configuration settings not found!", component)
        return component_configurations_xml

    def convert_xml_to_dictionary(self, xml):
        """Wrapper for converting xml to dictionary"""
        return self.__parser.convert_xml2dict(xml)

    def get_configuration_settings(self, component, configuration_file=None):
        """Returns the specified component_configuration settings from
         the ``configuration_file``.
        """
        if configuration_file is None:
            configuration_file = self.__configuration_file
        component_configurations_xml = self.load_xml(configuration_file, component)
        component_configurations_dict = self.convert_xml_to_dictionary(component_configurations_xml)
        return component_configurations_dict

    def load_log_configurations(self, name, directory=None,
                                configuration_settings=None):
        """Creates a logger with the specified name and configuration settings.

        Parameters
        ----------
        name : str
            Logger name

        directory: str
            target directory for the log file

        configuration_settings: dict
            configuration settings for the logger

        Returns
        ------
        Return a logger
        """
        if directory is None:
            # Case: if no directory is specified,
            # set the default directory for the logs
            target_directory = self.get_directory(directory='logs')
        else:
            # Case: make specified directory for the logs
            target_directory = self.make_directory(directory)
        if configuration_settings is None:
            log_configurations = self.get_configuration_settings(
                                                    'log_configurations')
        logger = ConfigLogger()
        return logger.initialize_logger(name, target_directory,
                                        configurations=log_configurations)


if __name__ == '__main__':
    # configure logger
    myLogger = ConfigurationsManager().load_log_configurations(__name__)
    # emit logs
    myLogger.info("configured!")
