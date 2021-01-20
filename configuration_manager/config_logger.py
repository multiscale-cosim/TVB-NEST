# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements; and to You under the Apache License,
#  Version 2.0."

import os
import logging
import logging.config
from functools import reduce
import operator


class ConfigLogger(object):
    """Creates loggers."""
    @classmethod
    def config_basic_settings(cls, name, target_directory):
        exit(1)  # TODO: add fallback configuration settings

    @classmethod
    def _set_in_dictionary(cls, xml_dictionary, mapList, value):
        cls._get_from_dictionary(xml_dictionary, mapList[:-1])[mapList[-1]] = value

    @classmethod
    def _get_from_dictionary(cls, xml_dictionary, mapList):
        return reduce(operator.getitem, mapList, xml_dictionary)

    @classmethod
    def _make_log_file(cls, target_directory, file_name):
        path = os.path.join(target_directory, file_name)
        return path

    @classmethod
    def __convert_xml_elements_datatypes(cls, xml_dictionary, target_directory):
        cls._set_in_dictionary(xml_dictionary, ['version'], 1)
        cls._set_in_dictionary(xml_dictionary, ['disable_existing_loggers'], False)
        cls._set_in_dictionary(xml_dictionary, ['loggers'], {})
        cls._set_in_dictionary(xml_dictionary, ['handlers', 'error_file',
                                                'filename'],
                                                cls._make_log_file(target_directory,
                                                "error_logs.logs"))
        cls._set_in_dictionary(xml_dictionary, ['handlers', 'info_file',
                                                'filename'],
                                                cls._make_log_file(target_directory,
                                                "info_logs.logs"))

    @classmethod
    def initialize_logger(cls, name, target_directory, xml_configurations=None):
        if xml_configurations is not None:
            cls.__convert_xml_elements_datatypes(xml_configurations, target_directory)
            logging.config.dictConfig(xml_configurations)
            return logging.getLogger(name)
        else:
            exit(1)  # TODO: better exception handling

