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
import pathlib

# Local imports
# adding the launcher root directory into the searching modules/packages path
# required when launcher is executed as module. i.e. python3 -m launcher
sys.path.insert(0, str(pathlib.Path(__file__).parent))
