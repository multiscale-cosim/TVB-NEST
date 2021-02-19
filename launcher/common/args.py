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
import argparse
from pathlib import Path


def xml_file_exists(path_and_filename=None):
    """

    :param path_and_filename: Location and XML filename defining the Co-Simulation Plan to be performed
    :return:
        None: when the file has not been found
        Location path plus filename when the file is reachable
    """
    return_value = None

    if Path(path_and_filename).is_file():
        return_value = path_and_filename
    else:
        raise argparse.ArgumentTypeError('{} is not reachable'.format(path_and_filename))

    return return_value


def arg_parse(args=None):
    """
        Parsing the command-line arguments passed to the launcher

        At least one is expected, the XML filename based on which the
        co-simulation processes will be launched
    :return:
        args
    """
    parser = argparse.ArgumentParser(prog='launcher',
                                     description='Launch a co-simulation experiment based on XML file',
                                     epilog='NOTE: on local system the MPI mpirun command will lunch the simulation;\n'
                                            'on SC cluster, the SLURM srun command will be used for such purpose.',
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        '--plan',
        '-p',
        help='XML file defining the co-simulation jobs to be launched',
        metavar='co_simulation_launch.xml',
        type=xml_file_exists,
        required=True,
    )

    args = parser.parse_args()

    return args
