# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements; and to You under the Apache License,
#  Version 2.0."

import os
import getpass
from pathlib import Path
from datetime import datetime
from utils import directory_utils
from default_directories_enum import DefaultDirectories

class MetaDirectoriesManager(type):
    """This metaclass ensures there exists only one instance of
    DirectoriesManager class. This prevents the side-effects such as
    the creation of multiple copies of output directories, concurrent
    access of DirectoriesManager class, and etc.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Case: First time instantiation.
            cls._instances[cls] = super(MetaDirectoriesManager,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DirectoriesManager(metaclass=MetaDirectoriesManager):

    def setup_default_directories(self, path) -> None:
        """ Setup default directories at specified location
        Default directories: Output, Output/Results, Output/Logs,
        Output/Figures, Output/Monitoring_Data.

        Parameters
        ----------
        path : str
            Location to setup the directories
        """

        # setup output directory at specified location
        output_dir = self.__setup_output_directory("outputs", path)
        # add default directory in dictionary
        self.__directories = ({DefaultDirectories.OUTPUT: output_dir})
        self.get_directory(DefaultDirectories.OUTPUT)
        # setup other default directories
        self.__directories.update({DefaultDirectories.LOGS:
                                  self.__make_default_directory(
                                      DefaultDirectories.LOGS.value)})
        self.__directories.update({DefaultDirectories.RESULTS:
                                  self.__make_default_directory(
                                      DefaultDirectories.RESULTS.value)})
        self.__directories.update({DefaultDirectories.FIGURES:
                                  self.__make_default_directory(
                                      DefaultDirectories.FIGURES.value)})
        self.__directories.update({DefaultDirectories.MONITORING_DATA:
                                  self.__make_default_directory(
                                      DefaultDirectories.MONITORING_DATA.value)})

    def get_directory(self, directory):
        """Returns the path for the specified directory.

        Raises `KeyError` if directory does not exist.
        """
        value = self.__directories.get(directory)
        if value:
            return self.__directories.get(directory)
        else:
            raise KeyError("directory not found!", directory)

    @staticmethod
    def __setup_output_directory(directory_name, path):
        """Creates the parent directory for outputs such as results,
        logs etc. at specified location.

        Parameters
        ----------
        directory_name : str
            Name for the Output directory

        path : str
            target location for setting up parent directory for the outputs

        Returns
        ------
        target_directory: str
            path to outputs directory
        """
        # get current user login name
        user_name = getpass.getuser()
        # using the current user login name and the timestamp to make it unique
        directory = user_name + '_' + directory_name + datetime.strftime(
            datetime.now(), '_%Y-%m-%d_%H%M%S')
        path = Path(path)
        target_directory = os.path.join(path, directory)
        directory_utils.safe_makedir(target_directory)
        return target_directory

    def make_directory(self, directory, path):
        """Safely makes the specified directory if it does not exist.

        Returns the path to the specified directory.
        """
        target_directory = os.path.join(path, directory)
        directory_utils.safe_makedir(target_directory)
        self.__directories.update({directory: target_directory})
        return target_directory

    def __make_default_directory(self, directory):
        """Safely makes the default directory.

        Returns the path to the target directory.
        """
        target_directory = os.path.join(self.get_directory(DefaultDirectories.OUTPUT), directory)
        directory_utils.safe_makedir(target_directory)
        return target_directory
