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
import mmap
import logging

from mpi4py import MPI

if __name__ == '__main__':

    results_dir = sys.argv[1]
    outputs_dir = sys.argv[2]  # location where the mmap file will be created
    mmap_filename = sys.argv[3]
    num_bytes = int(sys.argv[4])

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

    if not os.path.isdir(outputs_dir):
        logger.info('PPID={},PID={},{} does not exist'.format(process_PPID, process_PID, outputs_dir))
        exit(-1)

    mmap_path_filename = os.path.join(outputs_dir, mmap_filename)
    with open(mmap_path_filename, 'wb') as file_object:
        file_object.write(bytes(num_bytes))

    with open(mmap_path_filename, 'r+', encoding='utf8') as file_object:
        with mmap.mmap(file_object.fileno(), length=0, access=mmap.ACCESS_WRITE, offset=0) as mmap_object:
            # just checking the content
            assert bytes(num_bytes) == mmap_object[:num_bytes]

    logger.info('PPID={},PID={}, {} has been generated, {} bytes (0x00) written'.format(process_PPID,
                                                                                        process_PID,
                                                                                        mmap_path_filename,
                                                                                        num_bytes))

    exit(0)
