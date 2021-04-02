# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
from mpi4py import MPI
from nest_elephant_tvb.translation.mpi_io_ext import MPI_communication_extern

class MPI_communication(MPI_communication_extern):
    databuffer = None
    win = None
    ## writer of the buffer
    req_send_size = None
    access_buffer = None
    size_buffer = 0
    ## read of the buffer
    req_buffer = None

    def __init__(self,name,path,level_log,rank,buffer_r_w=None):
        super().__init__(name,path,level_log)
        self.rank = rank
        if buffer_r_w is not None:
            self._shared_mem_buffer(buffer_r_w)
            self.buffer_r_w = buffer_r_w
        else:
            self.buffer_r_w =None
        self.logger.info('MPI_communication: end MPI init')

    def finalise(self):
        self.logger.info("MPI_communication: finalise")
        if self.win is not None:
            MPI.Win.Free(self.win)
        super().finalise()
        self.logger.info("MPI_communication: end finalise")


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
        self.logger.info('MPI_communication: start creat buffer')
        datasize = MPI.DOUBLE.Get_size()
        bufsize = 1000000 * 3 # NOTE: hardcoded (max.expected events per package from nest)
        if buffer_r_w[1] == comm.Get_rank():
            bufbytes = datasize * bufsize
        else:
            bufbytes= 0
        self.logger.info('MPI_communication: allocate buffer')
        win = MPI.Win.Allocate_shared(bufbytes, datasize, comm=comm)
        self.logger.info('MPI_communication: start shared buffer')
        buf, datasize = win.Shared_query(buffer_r_w[1])
        self.logger.info('MPI_communication: shared buffer')
        assert datasize == MPI.DOUBLE.Get_size()
        self.logger.info('MPI_communication: variable buffer')
        # create a numpy array (buffer) whose data points to the shared mem
        self.databuffer = np.ndarray(buffer=buf, dtype='d', shape=(bufsize,))
        self.logger.info('MPI_communication: end create buffer')


    ## writter of the buffer

    def ready_write_buffer(self):
        status_ = MPI.Status()
        # wait until ready to receive new data (i.e. the sender has cleared the buffer)
        self.logger.info("MPI_communication: write(ready) : buffer size wait ")
        if self.req_send_size is not None:
            self.req_send_size.wait()
        self.size_buffer = 0  # head of the buffer, reset after each iteration
        self.logger.info("MPI_communication: write : buffer receive :"+str(self.rank)+" to "+str(self.buffer_r_w[0]))
        req_buffer = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[0])
        self.logger.info("MPI_communication: write(ready) : buffer receive wait")
        self.accept_buffer = req_buffer.wait(status_)
        self.logger.info("MPI_communication: write(ready) : buffer ready")


    def end_writing(self):
        self.logger.info("MPI_communication: write(end) : send size : " + str(self.size_buffer) +" rank "+str(self.rank)+" to "+str(self.buffer_r_w[0]))
        self.req_send_size = MPI.COMM_WORLD.isend(self.size_buffer, dest=self.buffer_r_w[0])
        self.logger.info("MPI_communication: write(end) : end")

    def release_write_buffer(self):
        self.logger.info("MPI_communication: write(release) : end sim")
        status_ = MPI.Status()
        # wait until ready to receive new data (i.e. the sender has cleared the buffer)
        self.logger.info("MPI_communication: write(release) : wait size")
        self.req_send_size.wait()
        if not self.access_buffer:
            self.logger.info("MPI_communication: write(release) : transmit end")
            req_buffer = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[0])
            self.logger.info("MPI_communication: write(release) : receive buffer accept")
            accept = req_buffer.wait(status_)
            self.logger.info("MPI_communication: write(release) : send  end rank"+str(self.rank)+" to "+str(self.buffer_r_w[1]))
            send_size = MPI.COMM_WORLD.isend(-1, dest=self.buffer_r_w[0])
            send_size.wait(status_)
        self.logger.info("MPI_communication: write(release) : end")

    ## reader fo the buffer

    def ready_to_read(self):
        self.logger.info("MPI_communication: read(ready) : begin")
        status_ = MPI.Status()
        # wait until the receiver has cleared the buffer, i.e. filled with new data
        self.logger.info("MPI_communication: read(ready) : wait buffer ready ")
        if self.req_buffer is None:
            self.logger.info('MPI_communication: read(ready) : start read buffer: '+str(self.rank)+" to "+str(self.buffer_r_w[1]))
            self.req_buffer = MPI.COMM_WORLD.isend(True, dest=self.buffer_r_w[1])
        self.req_buffer.wait()
        self.logger.info("MPI_communication: read(ready) : receive size : rank "+str(self.rank)+" from "+str(self.buffer_r_w[1]))
        send_state = MPI.COMM_WORLD.irecv( source=self.buffer_r_w[1])
        self.logger.info("MPI_communication: read(ready) : receive size wait")
        return send_state.wait(status=status_)

    def end_read(self):
        self.logger.info("MPI_communication: read(end) : end read buffer ")
        self.req_buffer = MPI.COMM_WORLD.isend(True, dest=self.buffer_r_w[1])
        self.logger.info("MPI_communication: read(end) : send end ")

    def release_read_buffer(self,size_buffer):
        self.logger.info("MPI_communication: read(release) : ending ")
        status_ = MPI.Status()
        self.req_buffer.wait()
        # disconnect when everything is ending
        if size_buffer != -1:
            self.logger.info("MPI_communication: read(release) : transmit end ")
            send_state = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[1])
            self.logger.info("MPI_communication: read(release) : receive end ")
            send_state.wait(status=status_)
            req_buffer = MPI.COMM_WORLD.isend(False, dest=self.buffer_r_w[1])
            self.logger.info("MPI_communication: read(release) : send end ")
            req_buffer.wait()
        self.logger.info("MPI_communication: read(release) : end ")
