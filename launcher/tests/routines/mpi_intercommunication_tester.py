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
import time
import logging
import mmap

from mpi4py import MPI

RETURN_OK = 0
RETURN_NOT_OK = -1

SERVER_OPERATION_MODE = 'server'
CLIENT_OPERATION_MODE = 'client'


class MemMap:
    #
    PORT_LENGTH_LOC = 0
    PORT_LENGTH_LENGTH = 1

    #
    PORT_NAME_LOC = 1
    PORT_NAME_LENGTH = 0  # to be set on run time


class MpiTcpInterCommunicator(object):

    def __init__(self,
                 MPI_COMM_WORLD,
                 MPI_COMM_SELF,
                 results_dir=None,
                 outputs_dir=None,
                 mmap_filename=None,
                 mpi_message_tag=None,
                 ping_value=None,
                 pong_value=None,
                 operation_mode=None):
        self.__results_dir = results_dir
        self.__outputs_dir = outputs_dir
        self.__mmap_filename = mmap_filename
        self.__mmap_path_filename = os.path.join(self.__outputs_dir, self.__mmap_filename)
        self.__mpi_message_tag = mpi_message_tag
        self.__ping_value = ping_value
        self.__pong_value = pong_value
        self.__operation_mode = operation_mode

        self.__logger = logging.getLogger()
        self.__logger.addHandler(logging.StreamHandler(sys.stdout))

        self.__logger.setLevel(logging.INFO)
        self.__logger.debug(sys.argv)

        self.__MPI_COMM_WORLD = MPI_COMM_WORLD  # creator's parameter
        self.__MPI_COMM_SELF = MPI_COMM_SELF  # creator's parameter
        self.__mpi_cw_size = self.__MPI_COMM_WORLD.Get_size()
        self.__mpi_cw_rank = self.__MPI_COMM_WORLD.Get_rank()
        self.__mpi_proc_name = MPI.Get_processor_name()

        self.__label = '{},rank={},processor={},PPID={},PID={}'.format(operation_mode,
                                                                       self.__mpi_cw_rank,
                                                                       self.__mpi_proc_name,
                                                                       os.getppid(),
                                                                       os.getpid())

        self.__mpi_info = MPI.INFO_NULL
        self.__mpi_port_name = None
        self.__mpi_port_name_length = 0
        self.__mpi_root = 0
        self.__mpi_comm = None
        self.__mpi_expected_source = MPI.PROC_NULL  # to avoid ranks != 0 to catch the receiving message

        self.__errhandler_world = self.__MPI_COMM_WORLD.Get_errhandler()
        self.__MPI_COMM_WORLD.Set_errhandler(MPI.ERRORS_RETURN)
        self.__errhandler = self.__MPI_COMM_SELF.Get_errhandler()
        self.__MPI_COMM_SELF.Set_errhandler(MPI.ERRORS_RETURN)

    def __del__(self):
        self.__MPI_COMM_WORLD.Set_errhandler(self.__errhandler_world)
        self.__errhandler_world.Free()
        self.__MPI_COMM_SELF.Set_errhandler(self.__errhandler)
        self.__errhandler.Free()

    def info(self, message_to_be_logged):
        self.__logger.info('{}: {}'.format(self.__label, message_to_be_logged))

    def error(self, message_to_be_logged=None):
        self.__logger.info('{}, ERROR: {}'.format(self.__label, message_to_be_logged))

    def report_mpi_error(self, mpi_ierr=None, mpi_operation_name=None):
        self.error('{} error  class: {}'.format(mpi_operation_name, mpi_ierr.Get_error_class()))
        self.error('{} error   code: {}'.format(mpi_operation_name, mpi_ierr.Get_error_code()))
        self.error('{} error string: {}'.format(mpi_operation_name, mpi_ierr.Get_error_string()))

    def __server(self):
        """
            Server side logic for the client/server MPI communication approach
            NOTE: check notes below where the method is called
        Returns:

        """
        if self.__mpi_cw_rank == 0:
            try:
                file_object = open(self.__mmap_path_filename, 'rb+')
            except FileNotFoundError:
                self.error('{} could not be opened'.format(self.__mmap_path_filename))
                return RETURN_NOT_OK

            try:
                mmap_object = mmap.mmap(file_object.fileno(), length=0, access=mmap.ACCESS_WRITE, offset=0)
            except SyntaxError:
                self.error('{} could not be mmaped'.format(self.__mmap_path_filename))
                return RETURN_NOT_OK

            # Open Listening Port
            try:
                self.__mpi_info = MPI.INFO_NULL
                self.__mpi_port_name = MPI.Open_port(self.__mpi_info)
                self.__mpi_port_name_length = len(self.__mpi_port_name)
            except MPI.Exception as ierr:
                self.report_mpi_error(mpi_ierr=ierr, mpi_operation_name='MPI.Open_port')
                return RETURN_NOT_OK

            # publishing the port name by means of the mmaped file
            mmap_object.seek(0)
            mmap_object[MemMap.PORT_LENGTH_LOC:MemMap.PORT_LENGTH_LENGTH] = \
                self.__mpi_port_name_length.to_bytes(length=MemMap.PORT_LENGTH_LENGTH, byteorder='big')

            mmap_object[MemMap.PORT_NAME_LOC:MemMap.PORT_NAME_LOC + self.__mpi_port_name_length] = \
                bytes('{}'.format(self.__mpi_port_name), 'utf8', )
            mmap_object.flush()

            #
            self.__mpi_expected_source = 0
        else:
            self.__mpi_expected_source = MPI.PROC_NULL

        self.info('waiting for client connection {}'.format(self.__mpi_port_name))
        self.__mpi_comm = self.__MPI_COMM_WORLD.Accept(self.__mpi_port_name,
                                                       self.__mpi_info,
                                                       self.__mpi_root)

        self.info('client connected, waiting for PING value')
        ping_value = self.__mpi_comm.recv(source=self.__mpi_expected_source, tag=self.__mpi_message_tag)

        if self.__mpi_cw_rank == 0:
            if ping_value == self.__ping_value:
                self.info('Gotten expected PING value {} from client'.format(ping_value))
            else:
                self.info('expected PING value from client should be {}, received {}'.format(self.__ping_value,
                                                                                             ping_value))
                self.__mpi_comm.Disconnect()
                return RETURN_NOT_OK
        else:
            # finishing server running on rank > 0 MPI processes
            self.info('Gotten {} from client'.format(ping_value))
            return RETURN_OK


        self.info('sending PONG value')
        self.__mpi_comm.send(self.__pong_value, dest=0, tag=self.__mpi_message_tag)

        while True:
            self.info('Waiting for the poison pill')
            poison_pill = self.__mpi_comm.recv(source=self.__mpi_expected_source, tag=self.__mpi_message_tag)

            if poison_pill is None:
                break

            self.info('by waiting for poison pill, {} was received'.format(poison_pill))

        self.__mpi_comm.Disconnect()

        if self.__mpi_cw_rank == 0:
            MPI.Close_port(self.__mpi_port_name)
        self.info('Server Processing Done')

        return RETURN_OK

    def __client(self):
        try:
            file_object = open(self.__mmap_path_filename, 'rb')
        except FileNotFoundError:
            self.error('{} could not be opened'.format(self.__mmap_path_filename))
            return RETURN_NOT_OK

        try:
            # ACCESS_READ
            mmap_object = mmap.mmap(file_object.fileno(), length=0, access=mmap.ACCESS_READ, offset=0)
        except SyntaxError:
            self.error('{} could not be mmaped'.format(self.__mmap_path_filename))
            return RETURN_NOT_OK

        # getting the MPI port name
        while True:
            self.__mpi_port_name_length = \
                int.from_bytes(mmap_object[MemMap.PORT_LENGTH_LOC:MemMap.PORT_LENGTH_LENGTH], 'big')
            if not self.__mpi_port_name_length == 0:
                break
            os.sched_yield()

        self.__mpi_port_name = \
            mmap_object[MemMap.PORT_NAME_LOC:MemMap.PORT_NAME_LOC + self.__mpi_port_name_length].decode()
        self.info('using the server port {}'.format(self.__mpi_port_name))

        # Attaching to the Listening Port
        try:
            self.__mpi_info = MPI.INFO_NULL
            # self.__mpi_comm = self.__MPI_COMM_WORLD.Connect(self.__mpi_port_name, self.__mpi_info, self.__mpi_root)
            self.__mpi_comm = self.__MPI_COMM_WORLD.Connect(self.__mpi_port_name, MPI.INFO_NULL, root=0)
            self.info('connected to the server')
        except MPI.Exception as ierr:
            self.report_mpi_error(mpi_ierr=ierr, mpi_operation_name='self.__MPI_COMM_WORLD.Connect')
            return RETURN_NOT_OK

        self.info('sending PING value')
        self.__mpi_comm.send(self.__ping_value, dest=0, tag=self.__mpi_message_tag)

        self.info('waiting for PONG value from the server')
        pong_value = self.__mpi_comm.recv(source=0, tag=self.__mpi_message_tag)
        if pong_value == self.__pong_value:
            self.info('Gotten expected PONG value {} from SERVER'.format(pong_value))
        else:
            self.info('expected PONG value from SERVER should be {}, received {}'.format(self.__pong_value,
                                                                                         pong_value))
            self.__mpi_comm.send(None, dest=0, tag=self.__mpi_message_tag)  # poison pill
            self.__mpi_comm.Disconnect()
            return RETURN_NOT_OK

        # sending some random value
        self.__mpi_comm.send(time.time_ns(), dest=0, tag=self.__mpi_message_tag)

        self.info('Sending poison pill to the SERVER')
        self.__mpi_comm.send(None, dest=0, tag=self.__mpi_message_tag)

        self.__mpi_comm.Disconnect()
        return RETURN_OK

    def run(self):

        self.info('MPI.size={},MPI.rank={},MPI.processor_name={}'.format(self.__mpi_cw_size,
                                                                         self.__mpi_cw_rank,
                                                                         self.__mpi_proc_name))

        if self.__mpi_cw_rank == 0:
            if not os.path.isdir(self.__results_dir):
                self.info('{} does not exist'.format(self.__results_dir))
                return RETURN_NOT_OK

            if not os.path.isdir(self.__outputs_dir):
                self.info('{} does not exist'.format(self.__outputs_dir))
                return RETURN_NOT_OK

        if self.__operation_mode == SERVER_OPERATION_MODE:
            # IMPORTANT:
            #           The MPI process on rank == 0 does:
            #             i. create the mmap file to be shared
            #            ii. fill such file up with the MPI's port name returned by MPI.Open_port
            #           iii. set 0 to the value of SOURCE to be used when recv is called
            #            iv. Close the opened port after processing
            #
            # WARNING: The MPI processes on rank != 0 just follow the same logic
            #          of the MPI process runing on rank == 0, nevertheless
            #          the MPI.PROC_NULL is set to the SOURCE to be used when recv is called
            #          otherwise the client/server approach become "frozen"
            return self.__server()

        elif self.__operation_mode == CLIENT_OPERATION_MODE:
            if self.__mpi_cw_rank == 0:
                return self.__client()
        else:
            self.error('not supported operation mode, <server|client>')
            return RETURN_NOT_OK

        self.info('{} finished'.format(self.__label))

        return RETURN_OK


def main():
    results_dir = sys.argv[1]
    outputs_dir = sys.argv[2]
    mmap_filename = sys.argv[3]  # located on results directory
    operation_mode = sys.argv[4]
    mpi_message_tag = int(sys.argv[5])
    ping_value = float(sys.argv[6])
    pong_value = float(sys.argv[7])

    if operation_mode == SERVER_OPERATION_MODE:
        mpi_server = MpiTcpInterCommunicator(MPI.COMM_WORLD,
                                             MPI.COMM_SELF,
                                             results_dir=results_dir,
                                             outputs_dir=outputs_dir,
                                             mmap_filename=mmap_filename,
                                             mpi_message_tag=mpi_message_tag,
                                             ping_value=ping_value,
                                             pong_value=pong_value,
                                             operation_mode=SERVER_OPERATION_MODE)
        return mpi_server.run()

    elif operation_mode == CLIENT_OPERATION_MODE:
        # forcing to run the client only by using one MPI process.
        assert MPI.COMM_WORLD.Get_size() == 1

        mpi_client = MpiTcpInterCommunicator(MPI.COMM_WORLD,
                                             MPI.COMM_SELF,
                                             results_dir=results_dir,
                                             outputs_dir=outputs_dir,
                                             mmap_filename=mmap_filename,
                                             mpi_message_tag=mpi_message_tag,
                                             ping_value=ping_value,
                                             pong_value=pong_value,
                                             operation_mode=CLIENT_OPERATION_MODE)
        return mpi_client.run()
    else:
        print('Operation Mode not supported. Please use <server|client>')
        return RETURN_NOT_OK


if __name__ == '__main__':
    exit(main())
