# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import time
import numpy as np
from mpi4py import MPI
import pathlib
import os
from nest_elephant_tvb.translation.utils import create_logger

class MPI_communication:
    databuffer = None
    win = None
    ## writer of the buffer
    req_send_size = None
    access_buffer = None
    size_buffer = 0
    ## read of the buffer
    req_buffer = None

    def __init__(self,name,path,level_log,rank,buffer_r_w=None):
        self.logger = create_logger(path,name, level_log)
        self.rank = rank
        self.name = name
        self.ports = []
        self.path_ports = []
        if buffer_r_w is not None:
            self._shared_mem_buffer(buffer_r_w)
            self.buffer_r_w = buffer_r_w
        else:
            self.buffer_r_w =None
        self.logger.info('end MPI init')

    def run(self,path_connection):
        if path_connection is not None:
            self.logger.info('create connection')
            self.create_connection(path_connection)
        self.simulation_time()
        if path_connection is not None:
            self.close_connection()
        self.finalise()

    def create_connection(self,paths,info=MPI.INFO_NULL,comm=MPI.COMM_SELF):
        '''
        MPI inter communicator to NEST

        '''
        self.logger.info('Translate Receive: before open_port')
        ### Connection to simulation (incoming data)
        port = MPI.Open_port(info)
        self.ports.append(port)
        for path in paths:
            self.logger.info('Translate '+self.name+': after open_port: ' + port)
            # Write file configuration of the port
            fport = open(path, "w+")
            fport.write(port)
            fport.close()
            pathlib.Path(path + '.unlock').touch()
            self.logger.info('Translate '+self.name+': path_file: ' + path)
            self.path_ports.append(path)
            self.logger.info('Wait for Translate : '+port)
        self.port_comm = comm.Accept(port, info, 0)
        self.logger.info('Connection accepted')

    def simulation_time(self,*args):
        raise Exception('not yet implemented')

    def close_connection(self):
        self.logger.info("close connection")
        for port in self.ports:
            MPI.Close_port(port)
        for path in self.path_ports:
            os.remove(path)
        self.port_comm.Disconnect()

    def finalise(self):
        self.logger.info("finalise")
        if self.win is not None:
            MPI.Win.Free(self.win)
        MPI.Finalize()


    def _shared_mem_buffer(self,buffer_r_w,comm=MPI.COMM_WORLD):
        '''
        Create shared memory buffer. MPI One-sided-Communication.
        :param comm: MPI intra communicator to create the buffer.
        :return buffer: 1D shared memory buffer array

        TODO: Buffersize/max. expected number of events hardcoded
        -> free param, handle properly!
        Explanation:
        -> each package from NEST contains a continuous list of the events of the current simulation step
        -> the number of events in each package is unknown and not constant
        -> each event is three doubles: Id_recording_device, neuronID, spiketimes

        TODO: reshaping of the buffer content is done in the science part
        -> 1D array to shape (x,3) where x is the number of events.
        -> this is decided by the nest I/O part, i.e. nest sends out events in 1D array
        -> can/should this be more generic?
        '''
        self.logger.info('start creat buffer')
        datasize = MPI.DOUBLE.Get_size()
        bufsize = 1000000 * 3 # NOTE: hardcoded (max.expected events per package from nest)
        if buffer_r_w[1] == comm.Get_rank():
            bufbytes = datasize * bufsize
        else:
            bufbytes= 0
        self.logger.info('allocate buffer')
        win = MPI.Win.Allocate_shared(bufbytes, datasize, comm=comm)
        self.logger.info('start shared buffer')
        buf, datasize = win.Shared_query(buffer_r_w[1])
        self.logger.info('shared buffer')
        assert datasize == MPI.DOUBLE.Get_size()
        self.logger.info('variable buffer')
        # create a numpy array (buffer) whose data points to the shared mem
        self.databuffer = np.ndarray(buffer=buf, dtype='d', shape=(bufsize,))


    ## writter of the buffer

    def ready_write_buffer(self):
        status_ = MPI.Status()
        # wait until ready to receive new data (i.e. the sender has cleared the buffer)
        self.logger.info(" write : buffer size wait ")
        if self.req_send_size is not None:
            self.req_send_size.wait()
        self.size_buffer = 0  # head of the buffer, reset after each iteration
        self.logger.info(" write : buffer receive :"+str(self.rank)+" to "+str(self.buffer_r_w[0]))
        req_buffer = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[0])
        self.logger.info(" write : buffer receive wait")
        self.accept_buffer = req_buffer.wait(status_)
        self.logger.info("buffer ready")


    def end_writing(self):
        self.logger.info(" write : send size : " + str(self.size_buffer))
        self.req_send_size = MPI.COMM_WORLD.isend(self.size_buffer, dest=self.buffer_r_w[0])

    def release_write_buffer(self):
        status_ = MPI.Status()
        # wait until ready to receive new data (i.e. the sender has cleared the buffer)
        self.req_send_size.wait()
        if not self.access_buffer:
            req_buffer = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[0])
            accept = req_buffer.wait(status_)
            send_size = MPI.COMM_WORLD.isend(-1, dest=self.buffer_r_w[0])
            send_size.wait(status_)

    ## reader fo the buffer

    def ready_to_read(self):
        status_ = MPI.Status()
        # wait until the receiver has cleared the buffer, i.e. filled with new data
        self.logger.info("read : wait buffer ready ")
        if self.req_buffer is None:
            self.logger.info('start read buffer: '+str(self.rank)+" to "+str(self.buffer_r_w[1]))
            self.req_buffer = MPI.COMM_WORLD.isend(True, dest=self.buffer_r_w[1])
        self.req_buffer.wait()
        self.logger.info("read : receive size : "+str(self.rank)+" to "+str(self.buffer_r_w[1]))
        send_state = MPI.COMM_WORLD.irecv( source=self.buffer_r_w[1])
        self.logger.info("read: receive size wait")
        return send_state.wait(status=status_)

    def end_read(self):
        self.logger.info("end read buffer ")
        self.req_buffer = MPI.COMM_WORLD.isend(True, dest=self.buffer_r_w[1])

    def release_read_buffer(self,size_buffer):
        self.logger.info("release buffer ")
        status_ = MPI.Status()
        self.req_buffer.wait()
        # disconnect when everything is ending
        if size_buffer != -1:
            send_state = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[1])
            send_state.wait(status=status_)
            req_buffer = MPI.COMM_WORLD.isend(False, dest=self.buffer_r_w[1])
            req_buffer.wait()
