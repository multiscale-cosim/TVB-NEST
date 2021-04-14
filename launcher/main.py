#!/usr/bin/env python
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
# ------------------------------------------------------------------------------
import sys
import common


def main(args=None):
    """
    :desc: Entry point for Co-Simulation CoSimulator tool
    :param args: user command line arguments
    :return: CoSimulator's return code to be used as exit code by the bash environment
    """
    co_simulator = common.cosimulator.CoSimulator()
    co_simulator_rc = co_simulator.run(sys.argv)

    if co_simulator_rc == common.enums.CoSimulatorReturnCodes.OK:
        # finished properly!
        return common.enums.BashReturnCodes.SUCCESSFUL  # 0
    # something went wrong
    elif co_simulator_rc == common.enums.CoSimulatorReturnCodes.PARAMETER_ERROR:
        return common.enums.BashReturnCodes.CO_SIMULATOR_PARAMETER_ERROR
    elif co_simulator_rc == common.enums.CoSimulatorReturnCodes.VARIABLE_ERROR:
        return common.enums.BashReturnCodes.CO_SIMULATOR_VARIABLE_ERROR
    elif co_simulator_rc == common.enums.CoSimulatorReturnCodes.XML_ERROR:
        return common.enums.BashReturnCodes.CO_SIMULATOR_XML_ERROR
    elif co_simulator_rc == common.enums.CoSimulatorReturnCodes.LAUNCHER_ERROR:
        return common.enums.BashReturnCodes.LAUNCHER_ERROR
    else:
        return common.enums.BashReturnCodes.CO_SIMULATOR_ERROR


if __name__ == '__main__':
    sys.exit(main(sys.argv))
