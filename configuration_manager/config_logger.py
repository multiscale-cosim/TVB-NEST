# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor
#  license agreements; and to You under the Apache License, Version 2.0. "
# ------------------------------------------------------------------------------

import os
import logging
import logging.config
from utils import dictionary_utils


class ConfigLogger:
    """Creates logger."""

    def config_default_settings(self, name, target_directory):
        # TODO: add fallback settings
        raise NotImplementedError("logger fallback settings!")

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
        # set the version as 1 (logging.config API requirement)
        dictionary_utils.set_in_dictionary(xml_dictionary, ['version'], 1)
        # disable any existing logger
        dictionary_utils.set_in_dictionary(xml_dictionary, ['disable_existing_loggers']
                                           , False)
        dictionary_utils.set_in_dictionary(xml_dictionary, ['loggers'], {})
        # setup error logs file
        error_logs_file = cls._make_log_file(target_directory, "error_logs.logs")
        dictionary_utils.set_in_dictionary(xml_dictionary, ['handlers', 'error_file',
                                           'filename'], error_logs_file)
        # setup info logs file
        info_logs_file = cls._make_log_file(target_directory, "info_logs.logs")
        dictionary_utils.set_in_dictionary(xml_dictionary, ['handlers', 'info_file',
                                           'filename'], info_logs_file)

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
                raise e
            return logging.getLogger(name)
        else:
            cls.config_default_settings(cls, name, target_directory)
