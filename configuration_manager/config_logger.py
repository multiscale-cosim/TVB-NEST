# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements; and to You under the Apache License,
#  Version 2.0."

import os
import logging
import logging.config
from functools import reduce
import operator


class ConfigLogger:
    """Creates logger."""

    def config_default_settings(self, name, target_directory):
        # TODO: add fallback settings
        raise NotImplementedError("logger fallback settings!")

    @classmethod
    def _set_in_dictionary(cls, xml_dictionary, key_list, new_value):
        """Finds and replace the value for the ``key_list`` with the
        specified ``new_value``in the nested dictionary.

         Raises ``KeyError`` exception if the ``key_list`` is not found in dictionary.
         Raises ``TypeError`` exception if the ``key_list`` type mismatchs with dictionary.
         Raises ``IndexError`` exception if the ``key_list`` index is out of range.

          Examples:
          >>> sample_dictionary = {'handlers', {'console': {'class': 'logging.StreamHandler',
          ...                      'level': 'INFO', 'formatter': 'default', 'stream': 'ext://sys.stdout'},
          ...                       'info_file': {'class': 'logging.FileHandler', 'level': 'INFO',
          ...                       'formatter': 'verbose', 'filename': 'default_logs.log'}
          >>> set_in_dictionary(sample_dictionary, ['handlers', 'info_file', 'default_logs.log'], 'my_logs.log' )
          >>> print(sample_dictionary)
          {'handlers', {'console': {'class': 'logging.StreamHandler',
          ...                      'level': 'INFO', 'formatter': 'default', 'stream': 'ext://sys.stdout'},
                                   'info_file': {'class': 'logging.FileHandler', 'level': 'INFO',
                                     'formatter': 'verbose', 'filename': 'my_logs.log}
          >>> set_in_dictionary(sample_dictionary, ['handlers', 'formatter', 'new_formatter'], 'simple' )
          KeyError: 'new_formatter'
          >>> set_in_dictionary(sample_dictionary, ['version', '2',], 1 )
          'TypeError: string indices must be integers'
          >>> set_in_dictionary(sample_dictionary, ['version', 10,], 1 )
          IndexError: string index out of range
          >>> set_in_dictionary(sample_dictionary, ['version', 1,], 1 )
          TypeError: 'str' object does not support item assignment
         """

        # get the nested sub_dictionary for the specified depth
        nested_sub_dictionary = cls._get_from_dictionary(xml_dictionary, key_list[:-1])
        try:
            if nested_sub_dictionary[key_list[-1]]:
                # Case: if the specified key exists
                nested_sub_dictionary[key_list[-1]] = new_value
        except (KeyError, TypeError, IndexError) as e:
            raise e  # TODO: a better exception handling

    @classmethod
    def _get_from_dictionary(cls, xml_dictionary, key_list):
        """Finds the specified nested key into a dictionary.

        Raises ``KeyError`` exception if the ``key_list`` is not found in dictionary.
        Raises ``TypeError`` exception if the ``key_list`` type mismatches with dictionary.
        Raises ``IndexError`` exception if the ``key_list`` index is out of range.

        Parameters
        ----------
        xml_dictionary : dict
            nested data structure to find the value

        key_list : list
            the nested path

        Returns
        -------
        Returns the sub_dictionary matches with ``key_list``."""

        try:
            return reduce(operator.getitem, key_list, xml_dictionary)
        except (KeyError, TypeError, IndexError) as e:
            raise e  # TODO: a better exception handling

    @classmethod
    def _make_log_file(cls, target_directory,file_name):
        """ returns the specified log file at specified location."""

        path = os.path.join(target_directory, file_name)
        return path

    @classmethod
    def __make_logging_config_compatible(cls, xml_dictionary,
                                         target_directory):
        """Makes the logger settings compatible with the logging.config API.
        Also, sets the destination of logs to specified log file at specified location.
        """

        cls._set_in_dictionary(xml_dictionary, ['version'], 1)
        cls._set_in_dictionary(xml_dictionary, ['disable_existing_loggers'], False)
        cls._set_in_dictionary(xml_dictionary, ['loggers'], {})
        cls._set_in_dictionary(xml_dictionary, ['handlers', 'error_file',
                                                'filename'],
                               cls._make_log_file(target_directory,
                                                  "error_logs.logs"))
        cls._set_in_dictionary(xml_dictionary, ['handlers', 'info_file',
                                                'filename'], cls._make_log_file(target_directory, "info_logs.logs"))

    @classmethod
    def initialize_logger(cls, name, target_directory, configurations=None):
        """Returns the logger with specified name and specified settings."""

        if configurations is not None:
            cls.__make_logging_config_compatible(configurations,
                                                 target_directory)
            try:
                logging.config.dictConfig(configurations)
            except ValueError as e:
                # TODO: add fall back configuration settings
                # or a better exception handling
                raise e
            return logging.getLogger(name)
        else:
            cls.config_default_settings(cls, name, target_directory)
