# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements; and to You under the Apache License,
#  Version 2.0."

from __future__ import annotations
from xml_parser import Parser
from config_logger import ConfigLogger
from directories_manager import DirectoriesManager
from default_directories_enum import DefaultDirectories


class ConfigurationsManager:
    """Mediator to manage the configuration settings."""

    __directories_manager = DirectoriesManager()
    __parser = Parser()

    def setup_default_directories(self, directory) -> None:
        """Wrapper for setting up default directories"""
        return self.__directories_manager.setup_default_directories(directory)

    def make_directory(self, directory, directory_path=None):
        """Wrapper for making directories"""
        if directory_path is None:
            directory_path = self.get_default_directory(DefaultDirectories.OUTPUT)
        return self.__directories_manager.make_directory(directory, directory_path)

    def get_directory(self, directory):
        """Wrapper for retrieving directories"""
        return self.__directories_manager.get_directory(directory)

    def convert_xml_to_dictionary(self, xml):
        """Wrapper for converting xml to dictionary"""
        return self.__parser.convert_xml2dict(xml)

    def get_configuration_settings(self, component, configuration_file) -> dict:
        """Returns the configuration settings for the target component from
         the configuration_file.

        Parameters
        ----------
        component : str
            target component

        configuration_file: str
            configuration file which contains the target component's settings

        Returns
        ------
        component_configurations_dict: dict
            configuration settings for the target component
        """
        # load xml settings for the target component
        component_configurations_xml = self.__load_xml(component,
                                                       configuration_file)
        component_configurations_dict = self.convert_xml_to_dictionary(
            component_configurations_xml)
        return component_configurations_dict

    def __load_xml(self, component, configuration_file):
        """helper function for getting configuration settings of a component"""
        # loads the xml configuration file as an xml.etree.ElementTree
        global_configurations_xml_tree = self.__parser.load_xml(configuration_file)
        # get root element
        root = global_configurations_xml_tree.getroot()
        # find the xml configuration settings for the desired component
        component_configurations_xml = root.find(component)
        if component_configurations_xml is None:
            raise LookupError("configuration settings not found!", component)
        return component_configurations_xml

    def load_log_configurations(self, name, log_configurations,
                                directory=None, directory_path=None) -> Logger:
        """Creates a logger with the specified name and configuration settings.
        The default location will be set for the logs if either directory or
        directory path is not specified.

        Parameters
        ----------
        name : str
            Logger name

        log_configurations: dict
            configuration settings for the logger

        directory: str
            target directory for the logs

        directory_path: str
            target location for the logs directory

        Returns
        ------
        Return a logger
        """
        if directory and directory_path is not None:
            # Case: make directory at the target location for the logs
            target_directory = self.make_directory(directory, directory_path)
        else:
            # Case: if no directory or the directory path is specified,
            # set the default directory for the logs
            target_directory = self.get_directory(directory=DefaultDirectories.LOGS)
        logger = ConfigLogger()
        return logger.initialize_logger(name, target_directory,
                                        configurations=log_configurations)
