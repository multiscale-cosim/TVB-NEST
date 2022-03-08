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
import array
import logging
import mmap
import os
import sys
import time

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


class MpiP2PSocketCommunicator(object):

    def __init__(self,
                 MPI_COMM_WORLD,
                 MPI_COMM_SELF,
                 results_dir=None,
                 outputs_dir=None,
                 mmap_filename=None,
                 byte_value=None,
                 integer_value=None,
                 float_value=None,
                 operation_mode=None):

        self.__results_dir = results_dir
        self.__outputs_dir = outputs_dir
        self.__mmap_filename = mmap_filename
        self.__mmap_path_filename = os.path.join(self.__outputs_dir, self.__mmap_filename)
        self.__byte_data_value = byte_value
        self.__integer_data_value = integer_value
        self.__float_data_value = float_value
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
        self.__mpi_status = None
        self.__mpi_intercomm = None
        self.__mpi_expected_source = MPI.PROC_NULL  # to avoid ranks != 0 to catch the receiving message

        self.__errhandler_world = self.__MPI_COMM_WORLD.Get_errhandler()
        self.__MPI_COMM_WORLD.Set_errhandler(MPI.ERRORS_RETURN)
        self.__errhandler = self.__MPI_COMM_SELF.Get_errhandler()
        self.__MPI_COMM_SELF.Set_errhandler(MPI.ERRORS_RETURN)

        self.__wait_for_client = False
        self.__receive_subsequent_messages = False

        self.__COMMAND_TAG = 0
        self.__POISON_PILL_TAG = 2
        self.__INTEGER_DATA_TAG = 4
        self.__FLOAT_DATA_TAG = 8

        self.__NO_MORE_MESSAGES_COMMAND = 0
        self.__POISON_PILL_COMMAND = 1

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

    def __open_port_and_mmap_it(self):
        """
            Creates the socket port and stores the port info into a shared mmap file.
        :return:
        """
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

        return RETURN_OK

    def __server_main_loop(self):
        """
            Socket server main loop, waits for incoming clients and its messages,
            some client must inform for server ending, meaning, POISON PILL.
        :return:
        """
        self.__mpi_status = MPI.Status()
        recv_integer_buffer = array.array('i', [0])
        recv_float_buffer = array.array('f', [0])

        self.__wait_for_client = True
        while self.__wait_for_client:
            os.sched_yield()

            self.info(f'Server-side, waiting for a client on {self.__mpi_port_name}')

            self.__mpi_intercomm = self.__MPI_COMM_SELF.Accept(port_name=self.__mpi_port_name,
                                                               info=self.__mpi_info,
                                                               root=self.__mpi_root)

            self.__receive_subsequent_messages = True
            while self.__receive_subsequent_messages:
                os.sched_yield()
                message_source = None
                message_tag = None
                self.__mpi_intercomm.Probe(source=MPI.ANY_SOURCE,
                                           tag=MPI.ANY_TAG,
                                           status=self.__mpi_status)
                message_source = self.__mpi_status.Get_source()
                message_tag = self.__mpi_status.Get_tag()

                # the MPI.TAG defines how the server must proceed
                #
                #   COMMAND
                #
                if self.__COMMAND_TAG == message_tag:
                    # a command has been sent
                    self.__mpi_intercomm.Recv([recv_integer_buffer, MPI.INT],
                                              source=MPI.ANY_SOURCE,
                                              tag=MPI.ANY_TAG,
                                              status=self.__mpi_status)
                    command = recv_integer_buffer[0]
                    if self.__NO_MORE_MESSAGES_COMMAND == command:
                        #
                        # client has informed that there won't be more messages
                        #
                        self.__receive_subsequent_messages = False
                    else:
                        self.info(
                            f'Server-side, there is no implementation for tag={message_tag}, command={command}, from={message_source}')
                        #
                        # even though there is no a command implementation for the __COMMAND_TAG,
                        # the receiving messages loop will be finished
                        self.__receive_subsequent_messages = False
                #
                #   POISON PILL
                #
                elif self.__POISON_PILL_TAG == message_tag:
                    # the poison pill has been sent
                    self.__mpi_intercomm.Recv([recv_integer_buffer, MPI.INT],
                                              source=MPI.ANY_SOURCE,
                                              tag=MPI.ANY_TAG,
                                              status=self.__mpi_status)
                    command = recv_integer_buffer[0]

                    if self.__POISON_PILL_COMMAND == command:
                        # gotten request for stopping (POISON PILL)
                        self.info(
                            f'Server-side, POISON PILL has been gotten from source={message_source}, time to stop')
                        self.__receive_subsequent_messages = False
                        self.__wait_for_client = False  # no more Accept calls
                    else:
                        self.info(
                            f'Server-side, there is no implementation for tag={message_tag}, command={command}, from={message_source}')
                        #
                        # even tough there is no command implementation for the __POISON_PILL_TAG call,
                        # the receiving messages loop will be finished
                        self.__receive_subsequent_messages = False
                #
                # INTEGER
                #
                elif self.__INTEGER_DATA_TAG == message_tag:
                    self.__mpi_intercomm.Recv([recv_integer_buffer, MPI.INT],
                                              source=MPI.ANY_SOURCE,
                                              tag=MPI.ANY_TAG,
                                              status=self.__mpi_status)
                    self.info(f'Server-side, received INTEGER={recv_integer_buffer[0]}')
                #
                # FLOAT
                #
                elif self.__FLOAT_DATA_TAG == message_tag:
                    self.__mpi_intercomm.Recv([recv_float_buffer, MPI.FLOAT],
                                              source=MPI.ANY_SOURCE,
                                              tag=MPI.ANY_TAG,
                                              status=self.__mpi_status)
                    self.info(f'Server-side, received FLOAT={recv_float_buffer[0]}')
                #
                # BYTE BUFFER, since unknown TAG has been gotten
                #
                else:
                    # unknown tag, processing the message as a BYTE stream
                    count = self.__mpi_status.Get_count(MPI.BYTE)
                    elems = self.__mpi_status.Get_elements(MPI.BYTE)
                    buf = array.array('B', [0]) * count
                    self.__mpi_intercomm.Recv([buf, MPI.BYTE], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)  #, status=self.__mpi_status)
                    self.info(f'Server-side, unknown tag={message_tag}, from source={message_source}, gotten buf={buf}')

            #
            # Closing connection
            #
            self.__mpi_intercomm.Disconnect()

        return RETURN_OK

    def run_server_side(self):
        """
            Server side for testing the point-to-point MPI communication approach
        Returns:

        """
        # __debugging__ self.info(f'Server-side on rank={self.__mpi_cw_rank} started')

        if self.__mpi_cw_rank == 0:
            if RETURN_OK == self.__open_port_and_mmap_it():
                self.__server_main_loop()
                MPI.Close_port(self.__mpi_port_name)
            else:
                return RETURN_NOT_OK
        else:
            # finishing server running on rank > 0 MPI processes
            self.info(f'Server-side, nothing to be performed by server code running on rank={self.__mpi_cw_rank}')

        # __debugging__ self.info(f'Server-side on rank={self.__mpi_cw_rank} done')
        return RETURN_OK

    def __client_open_port_from_mmap(self):
        try:
            file_object = open(self.__mmap_path_filename, 'rb')
        except FileNotFoundError:
            self.error(f'{self.__mmap_path_filename} could not be opened')
            return RETURN_NOT_OK

        try:
            # ACCESS_READ
            mmap_object = mmap.mmap(file_object.fileno(), length=0, access=mmap.ACCESS_READ, offset=0)
        except SyntaxError:
            self.error(f'{self.__mmap_path_filename} could not be mmaped')
            return RETURN_NOT_OK

        # getting the MPI port name
        while True:
            os.sched_yield()
            self.__mpi_port_name_length = \
                int.from_bytes(mmap_object[MemMap.PORT_LENGTH_LOC:MemMap.PORT_LENGTH_LENGTH], 'big')
            if 0 == self.__mpi_port_name_length:
                continue
            break

        self.__mpi_port_name = \
            mmap_object[MemMap.PORT_NAME_LOC:MemMap.PORT_NAME_LOC + self.__mpi_port_name_length].decode()
        self.info(f'Client-side, using the server port {self.__mpi_port_name}')

        return RETURN_OK

    def __client_connect_to_the_port(self):
        """
            Establishing the connection to the already open port
        :return:
        """
        # Attaching to the Listening Port
        try:
            self.__mpi_info = MPI.INFO_NULL
            #
            # it works only when mpirun -np 1 ... is used
            #
            # self.__mpi_intercomm = self.__MPI_COMM_WORLD.Connect(self.__mpi_port_name, info=MPI.INFO_NULL, root=0)

            #
            # it works for point-to-point socket inter-communications
            #
            self.__mpi_intercomm = self.__MPI_COMM_SELF.Connect(self.__mpi_port_name, info=MPI.INFO_NULL, root=0)
            self.info('Client-side, connected to the server')
        except MPI.Exception as ierr:
            self.report_mpi_error(mpi_ierr=ierr, mpi_operation_name='self.__MPI_COMM_SELF.Connect')
            return RETURN_NOT_OK

        return RETURN_OK

    def __client_send_data(self):
        """
            Sending data to socket-server side
        :return:
        """

        if RETURN_NOT_OK == self.__client_connect_to_the_port():
            return RETURN_NOT_OK

        #
        # INTEGER
        #
        send_integer_buffer = array.array('i', [0])

        send_integer_buffer[0] = self.__integer_data_value
        self.__mpi_intercomm.Send([send_integer_buffer, MPI.INT], dest=0, tag=self.__INTEGER_DATA_TAG)
        self.info(f'Client-side, INTEGER={self.__integer_data_value} has been sent')

        # 
        # FLOAT
        #
        send_float_buffer = array.array('f', [0])

        send_float_buffer[0] = self.__float_data_value
        self.__mpi_intercomm.Send([send_float_buffer, MPI.FLOAT], dest=0, tag=self.__FLOAT_DATA_TAG)
        self.info(f'Client-side, FLOAT={self.__float_data_value} has been sent')

        #
        # BYTE
        #
        send_byte_buffer = array.array('B')
        size = len(self.__byte_data_value)
        send_byte_buffer.frombytes(self.__byte_data_value.encode('UTF-8'))
        self.__mpi_intercomm.Send([send_byte_buffer, size, MPI.BYTE], dest=0, tag=666)
        self.info(f'Client-side, BYTE BUFFER={self.__byte_data_value} has been sent')

        #
        # Here a dataset could be sent by means of a loop
        #
        #
        # no more messages (data) to be sent
        #
        send_integer_buffer[0] = self.__NO_MORE_MESSAGES_COMMAND
        self.__mpi_intercomm.Send([send_integer_buffer, MPI.INT], dest=0, tag=self.__COMMAND_TAG)
        self.__mpi_intercomm.Disconnect()

        return RETURN_OK

    def __client_send_poison_pill(self):
        """
            Sending the POISON PILL to the socket-server side in order to stop it
        :return:
        """
        self.info(f'Client-side on rank={self.__mpi_cw_rank} will send POISON PILL')

        if RETURN_NOT_OK == self.__client_connect_to_the_port():
            return RETURN_NOT_OK
        #
        # POISON PILL
        #
        send_poison_pill_buffer = array.array('i', [0])
        send_poison_pill_buffer[0] = self.__POISON_PILL_COMMAND
        self.__mpi_intercomm.Send([send_poison_pill_buffer, MPI.INT], dest=0, tag=self.__POISON_PILL_TAG)
        self.__mpi_intercomm.Disconnect()
        return RETURN_OK

    def run_client_side(self):
        """
            Client side of the point-to-point communication
        :return:
        """
        self.info(f'Client-side on rank={self.__mpi_cw_rank} started')

        if self.__mpi_cw_rank == 0:
            if RETURN_OK == self.__client_open_port_from_mmap():
                self.__client_send_data()
                self.__client_send_poison_pill()
                MPI.Close_port(self.__mpi_port_name)
            else:
                self.info(f'Client-side, something went wrong getting port from mmap or opening the socket port')
                return RETURN_NOT_OK
        else:
            #
            self.info(f'Client-side, nothing to be performed by client side running on rank={self.__mpi_cw_rank}')

        self.info(f'Client-side on rank={self.__mpi_cw_rank} done')
        return RETURN_OK


def main():
    results_dir = sys.argv[1]
    outputs_dir = sys.argv[2]
    mmap_filename = sys.argv[3]  # located on results directory
    operation_mode = sys.argv[4]

    if operation_mode == SERVER_OPERATION_MODE:
        mpi_p2p_socket_server = MpiP2PSocketCommunicator(MPI.COMM_WORLD,
                                                         MPI.COMM_SELF,
                                                         results_dir=results_dir,
                                                         outputs_dir=outputs_dir,
                                                         mmap_filename=mmap_filename)
        return mpi_p2p_socket_server.run_server_side()

    elif operation_mode == CLIENT_OPERATION_MODE:
        byte_value = sys.argv[5]
        integer_value = int(sys.argv[6])
        float_value = float(sys.argv[7])

        mpi_p2p_socket_client = MpiP2PSocketCommunicator(MPI.COMM_WORLD,
                                                         MPI.COMM_SELF,
                                                         results_dir=results_dir,
                                                         outputs_dir=outputs_dir,
                                                         mmap_filename=mmap_filename,
                                                         byte_value=byte_value,
                                                         integer_value=integer_value,
                                                         float_value=float_value,
                                                         operation_mode=CLIENT_OPERATION_MODE)
        return mpi_p2p_socket_client.run_client_side()

    else:
        print('Operation Mode not supported. Please use <server|client>')
        return RETURN_NOT_OK


if __name__ == '__main__':
    exit(main())
