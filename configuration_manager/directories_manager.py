# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements; and to You under the Apache License,
#  Version 2.0."

import os
from utils.util import safe_makedir
from datetime import datetime
from definitions import OUTPUT_DIR


class MetaDirectoriesManager(type):
    """This metaclass ensures there exists only one instance of
    DirectoriesManager class. This prevents the side-effects such as
    the creation of multiple copies of output directories, concurrent
    access of DirectoriesManager class, and etc.
    """
    _instances = {}
    __directories = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # Case: First time instantiation.
            cls._instances[cls] = super(MetaDirectoriesManager,
                                        cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DirectoriesManager(metaclass=MetaDirectoriesManager):

    def __init__(self):
        # create default directories
        self.__directories = ({'output': self.__setup_output_directory(OUTPUT_DIR)})
        self.__directories.update({'logs': self.make_directory('logs')})
        self.__directories.update({'results': self.make_directory('results')})

    def get_directory(self, directory):
        """Returns the path for the specified directory.
        
        Raises `KeyError` if directory does not exist.
        """
        value = self.__directories.get(directory)
        if value:
            return self.__directories.get(directory)
        else:
            # TODO: a better exception handling
            raise KeyError("directory not found!", directory)

    @staticmethod
    def __setup_output_directory(name):
        """Creates output directory for results, logs etc.

        Parameters
        ----------
        name : str
            Name for the Output directory

        Returns
        ------
        target_directory: str
            Output directory path
        """

        target_directory = name + datetime.strftime(datetime.now(),
                                                    '_%Y-%m-%d_%H-%M')
        safe_makedir(target_directory)
        return target_directory

    def make_directory(self, directory):
        """Safely makes the specified directory if it does not exist.

        Returns the path to the specified directory.
        """
        target_directory = os.path.join(self.get_directory('output'), directory)
        safe_makedir(target_directory)
        self.__directories.update({directory: target_directory})
        return target_directory
