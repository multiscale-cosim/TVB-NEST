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
import json
import logging

from mpi4py import MPI

if __name__ == '__main__':

    results_dir = sys.argv[1]
    simple_test_dir = sys.argv[2]
    json_params_filename = sys.argv[3]

    process_PPID = os.getppid()
    process_PID = os.getpid()

    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))

    logger.setLevel(logging.INFO)
    logger.debug(sys.argv)

    mpi_cw_size = MPI.COMM_WORLD.Get_size()
    mpi_cw_rank = MPI.COMM_WORLD.Get_rank()
    mpi_proc_name = MPI.Get_processor_name()

    logger.info('PPID={},PID={},MPI.COMM_WORLD.size={},MPI.COMM_WORLD.rank={},MPI.processor_name={}'.format(
        process_PPID, process_PID, mpi_cw_size, mpi_cw_rank, mpi_proc_name))

    if not os.path.isdir(results_dir):
        logger.info('PPID={},PID={},{} does not exist'.format(process_PPID, process_PID, results_dir))
        exit(-1)

    if not os.path.isdir(simple_test_dir):
        logger.info('PPID={},PID={},{} does not exist'.format(process_PPID, process_PID, simple_test_dir))
        exit(-1)

    with open(os.path.join(results_dir, json_params_filename), 'r') as json_params_fd:
        json_params_content = json.load(json_params_fd)

    output_path_filename = os.path.join(simple_test_dir, '{}.output'.format(process_PID))

    with open(output_path_filename, 'w') as output_fd:
        output_fd.write('PPID={},PID={},MPI.COMM_WORLD.size={},MPI.COMM_WORLD.rank={},MPI.processor_name={}'.format(
            process_PPID, process_PID, mpi_cw_size, mpi_cw_rank, mpi_proc_name))
        output_fd.write(os.linesep)

        for key, value in json_params_content['json_root_object'].items():
            output_fd.write('{}={}'.format(key, value))
            output_fd.write(os.linesep)

    logger.info('PPID={}, PID={}, {} has been generated'.format(process_PPID,
                                                                process_PID,
                                                                output_path_filename))
    exit(0)
