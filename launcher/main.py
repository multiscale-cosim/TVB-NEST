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
#   Date: 2021.02.16
# ------------------------------------------------------------------------------
import sys
import common


def main(args=None):
    """
    :desc: Entry point for Co-Simulation Launcher tool
    :param args: user command line arguments
    :return: Launcher's return code to be used as exit code by the bash environment
    """
    launcher = common.launcher.Launcher()

    # launcher_rc = common.launcher.Launcher.run(sys.argv)
    launcher_rc = launcher.run(sys.argv)

    if launcher_rc == common.enums.LauncherReturnCodes.PARAMETER_ERROR:
        return common.enums.BashReturnCodes.LAUNCHER_PARAMETER_ERROR
    elif launcher_rc == common.enums.LauncherReturnCodes.XML_ERROR:
        return common.enums.BashReturnCodes.LAUNCHER_XML_ERROR
    elif launcher_rc == common.enums.LauncherReturnCodes.NOT_OK:
        return common.enums.BashReturnCodes.LAUNCHER_ERROR

    return common.enums.BashReturnCodes.SUCCESSFUL  # 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
