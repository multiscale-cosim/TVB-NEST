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
import os
import sys
import numpy
import logging


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logger.debug(sys.argv)

    output_file = os.path.join(sys.argv[1], sys.argv[2])
    output_array = numpy.zeros((110, 1))
    numpy.save(file=output_file, arr=output_array)

    logger.info('{} has been generated on {}'.format(sys.argv[1], sys.argv[2]))

