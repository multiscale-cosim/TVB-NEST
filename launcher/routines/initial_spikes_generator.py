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
    # TO BE DONE: arguments validation
    output_path = sys.argv[1]
    output_file = sys.argv[2]

    process_PPID = os.getppid()
    process_PID = os.getpid()

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))

    # TO BE DONE: as a command line argument the logging level should be set
    logger.setLevel(logging.INFO)
    logger.debug(sys.argv)

    output_path_filename = os.path.join(output_path, output_file)
    output_array = numpy.zeros((110, 1))

    numpy.save(file=output_path_filename, arr=output_array)

    logger.info('PPID={}, PID={}, {} has been generated'.format(process_PPID,
                                                                process_PID,
                                                                output_path_filename))


