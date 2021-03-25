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
import enum


@enum.unique
class ActionReturnCodes(enum.Enum):
    """
        Class implementing the general enumerations to be used by the Action class
    """
    # General return codes
    OK = 0
    NOT_OK = -1

    OS_ERROR_EXCEPTION = 10
    VALUE_ERROR_EXCEPTION = 20


@enum.unique
class CoSimulatorReturnCodes(enum.Enum):
    """
        Class implementing the general enumerations to be used through whole CoSimulator tool

        NOTE: Value are oriented to be checked by bash environment
                where a return value of ZERO means the command finished properly
    """
    # General return codes
    OK = 0
    NOT_OK = -1

    # Returns related to parameters JSON file
    JSON_FILE_ERROR = 5

    # Returns related to the Launcher component
    LAUNCHER_ERROR = 50

    # Returns code related to command-line parameters
    PARAMETER_ERROR = 105

    # Returns code related to Co-Simulation Environment Variables
    VARIABLE_ERROR = 150

    # Returns code related to Co-Simulation Action Plan XML File
    XML_ERROR = 205


@enum.unique
class BashReturnCodes(enum.IntEnum):
    """
        Class implementing the exit codes to be returned to the bash environment

        NOTE:
            Based on https://tldp.org/LDP/abs/html/exitcodes.html there are some
            reserved exit codes as follows:

            1       - Catchall for general errors
            2       - Misuse of shell builtins (according to Bash documentation)
            126     - Command invoked cannot execute
            127     - “command not found”
            128     - Invalid argument to exit
            128+n   - Fatal error signal “n”
            130     - Script terminated by Control-C
            255     - Exit status out of range
    """
    # Reporting everything was performed as expected
    SUCCESSFUL = 0

    # General Error
    CATCHALL_ERROR = 1  # Catchall for general errors
    __DO_NOT_USE__ = 2  # - Misuse of shell builtins (according to Bash documentation)

    # Co-Simulator 30-39
    CO_SIMULATOR_PARAMETER_ERROR = 33
    CO_SIMULATOR_VARIABLE_ERROR = 35
    CO_SIMULATOR_XML_ERROR = 37
    CO_SIMULATOR_ERROR = 39

    # Co-Simulation Orchestrator 50-59
    ORCHESTRATOR_WRONG_PARAMETER = 58
    ORCHESTRATOR_ERROR = 59

    # Co-Simulation Broker 70-79
    BROKER_ERROR = 79

    # Co-Simulation Launcher 90-99
    LAUNCHER_ERROR = 99

    # Operating Systems
    COMMAND_CANNOT_EXECUTE = 126  # - Command invoked cannot execute
    COMMAND_NOT_FOUND = 127  # - “command not found”
    INVALID_ARGUMENT_TO_EXIT = 128  # - Invalid argument to exit

    CONTROL_C_PRESSED = 130  # 128 + SIGINT (2)

    FATAL_ERROR_BY_SIGKILL = 137  # 128 + SIGKILL (9)
    FATAL_ERROR_BY_SIGTERM = 143  # 128 + SIGTERM (15)

    __OUT_OF_RANGE__ = 255  # - Exit status out of range


@enum.unique
class LauncherReturnCodes(enum.Enum):
    """
        Class implementing the general enumerations to be used through whole launcher tool
    """

    # General return codes
    LAUNCHER_OK = 0
    LAUNCHER_NOT_OK = -1

    # Return codes related to the grouping of the actions
    ACTIONS_GROUPING_ERROR = 10

    # Return codes reported when the XML filenames are gathered from the XML action plan file
    GATHERING_XML_FILENAMES_ERROR = 50

    # Return codes related to parameters JSON file
    JSON_FILE_ERROR = 110

    # Return codes related to mapping the action plan out
    MAPPING_OUT_ERROR = 120

    # Return codes related to command-line parameters
    PARAMETER_ERROR = 130

    # Return codes related to the execution of the action plan strategy
    PERFORMING_STRATEGY_ERROR = 140

    # Return codes related to preparing the arguments for the Popen call by using environment variables
    PREPARING_ARGUMENTS_ERROR = 160

    # Return codes related to the spawners processes
    STARTING_SPAWNERS_ERROR = 200

    # Return codes related to Co-Simulation Plan XML File
    XML_ERROR = 250


@enum.unique
class ParametersReturnCodes(enum.Enum):
    """
        Enum Class implementing the enumeration related to
        the validation of the run time Co-Simulation Parameters,
        i.e. those with the prefix CO_SIM_ in the <parameters> section
    """

    PARAMETER_OK = 0
    PARAMETER_NOT_OK = -1

    PARAMETER_NOT_FOUND = 10
    VALUE_NOT_SET = 20


@enum.unique
class VariablesReturnCodes(enum.Enum):
    """
        Enum Class implementing the enumeration related to
        the validation of the run time Co-Simulation Variables,
        i.e. those with the prefix CO_SIM_ in the <variables> section
    """

    VARIABLE_OK = 0
    VARIABLE_NOT_OK = -1

    VARIABLE_NOT_FOUND = 10
    VALUE_NOT_SET = 20


@enum.unique
class XmlManagerReturnCodes(enum.Enum):
    """
        Enum Class implementing the enumerations related to
        the validation of the Co-Simulation Plan XML input file
    """
    XML_OK = 0
    XML_CO_SIM_VARIABLE_ERROR = 200
    XML_ENVIRONMENT_VARIABLE_ERROR = 205
    XML_FORMAT_ERROR = 210
    XML_TAG_ERROR = 215
    XML_VALUE_ERROR = 220
    XML_WRONG_MANAGER_ERROR = 225
