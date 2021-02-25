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
#       Team: Multiscale Simulation and Design
#
#   Date: 2021.02.18
# ------------------------------------------------------------------------------
import enum


@enum.unique
class XmlManagerReturnCodes(enum.Enum):
    """
        Enum Class implementing the enumerations related to
        the validation of the Co-Simulation Plan XML input file
    """
    XML_OK = 0

    XML_FORMAT_ERROR = 201
    XML_TAG_ERROR = 202
    XML_VALUE_ERROR = 203
    XML_WRONG_MANAGER_ERROR = 204


@enum.unique
class LauncherReturnCodes(enum.Enum):
    """
        Class implementing the general enumerations to be used through whole launcher tool

        NOTE: Value are oriented to be checked by bash environment
                where a return value of ZERO means the command finished properly
    """
    # General return codes
    OK = 0
    NOT_OK = -1

    # Returns related to parameters JSON file
    JSON_FILE_ERROR = 5

    # Returns code related to command-line parameters
    PARAMETER_ERROR = 105

    # Returns code related to Co-Simulation Plan XML File
    XML_ERROR = 205


@enum.unique
class BashReturnCodes(enum.IntEnum):
    """
        Class implementing the exit codes to be returned to the bash environment

        NOTE:
            Based on https://tldp.org/LDP/abs/html/exitcodes.html there are some
            reserved exit codes as follows:

            1 - Catchall for general errors
            2 - Misuse of shell builtins (according to Bash documentation)
            126 - Command invoked cannot execute
            127 - “command not found”
            128 - Invalid argument to exit
            128+n - Fatal error signal “n”
            130 - Script terminated by Control-C
            255\* - Exit status out of range
    """
    # Reporting everything was performed as expected
    SUCCESSFUL = 0

    # General Error
    CATCHALL_ERROR = 1  # Catchall for general errors
    __DO_NOT_USE__ = 2  # - Misuse of shell builtins (according to Bash documentation)

    # Co-Simulation Broker 70-79
    BROKER_ERROR = 79

    # Co-Simulation Launcher 80-89
    LAUNCHER_PARAMETER_ERROR = 87
    LAUNCHER_XML_ERROR = 88
    LAUNCHER_ERROR = 89

    # Co-Simulation Orchestrator 90-99
    ORCHESTRATOR_WRONG_PARAMETER = 98
    ORCHESTRATOR_ERROR = 99

    # Operating Systems
    COMMAND_CANNOT_EXECUTE = 126  # - Command invoked cannot execute
    COMMAND_NOT_FOUND = 127  # - “command not found”
    INVALID_ARGUMENT_TO_EXIT = 128  # - Invalid argument to exit

    CONTROL_C_PRESSED = 130  # 128 + SIGINT (2)

    FATAL_ERROR_BY_SIGKILL = 137  # 128 + SIGKILL (9)
    FATAL_ERROR_BY_SIGTERM = 143  # 128 + SIGTERM (15)

    __OUT_OF_RANGE__ = 255  # - Exit status out of range
