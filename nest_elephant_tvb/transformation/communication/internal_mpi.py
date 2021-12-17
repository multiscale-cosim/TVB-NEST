#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import numpy as np
from nest_elephant_tvb.transformation.communication.internal import CommunicationInternAbstract


class MPICommunication(CommunicationInternAbstract):
    """
    Class for using MPI for the internal communication
    """

    def __init__(self, logger=None, buffer_r_w=None, sender_rank=None, receiver_rank=None, timer=None):
        """
        initialisation of MPI communication
        :param logger: logger for internal communication
        :param buffer_r_w: array of 2 ranks [ reader rank, writer rank]
        :param sender_rank: rank which will receive data
        :param receiver_rank: rank which send data
        """
        super().__init__(logger=logger, timer=timer)
        self.rank = MPI.COMM_WORLD.Get_rank()
        self.logger.info(
            'MPI Internal :rank ' + str(self.rank) + ' argument function logger :' + str(logger) + ' buffer: ' + str(
                buffer_r_w) + ' sender_rank: ' + str(sender_rank) + ' receiver_rank: ' + str(receiver_rank))
        # usage of shared memory
        self.win = None  # it's a MPI Window for shared buffer if it's required
        if buffer_r_w is not None:
            self._shared_mem_buffer(buffer_r_w)
            self.buffer_r_w = buffer_r_w
            # writer of the buffer
            self.request_send_size_buffer = None
            # read of the buffer
            self.request_read_buffer = None
        else:
            self.buffer_r_w = None
        self.logger.info('MPI Internal : buffer ' + str(buffer_r_w))
        # variable for rate
        if sender_rank is not None:
            self.sender_rank = sender_rank
            self.request_send_done = None
        self.logger.info('MPI Internal : init receive variable cond :' + str(receiver_rank is not None))
        if receiver_rank is not None:
            self.logger.info('MPI Internal : init receive variable')
            self.receiver_rank = receiver_rank
            self.request_receive_time = None
            self.request_receive_rate = None
            self.request_read_done = None
        self.logger.info('MPI Internal : end MPI init')

    def finalise(self):
        """
        see super class
        """
        self.logger.info("MPI Internal : finalise : begin")
        if self.win is not None:  # free windows if it's necessary
            MPI.Win.Free(self.win)
        self.logger.info("MPI Internal : finalise : end")
        return True  # return true because all the rank need to Finalise MPI

    def _shared_mem_buffer(self, buffer_r_w, comm=MPI.COMM_WORLD):
        """
        Create shared memory buffer.
        :param buffer_r_w : array of 2 ranks [ reader rank, writer rank]
        :param comm : MPI communication

        TODO: Buffersize/max. expected number of events hardcoded
        -> free param, handle properly!
        Explanation:
        -> each package from NEST contains a continuous list of the events of the current simulation step
        -> the number of events in each package is unknown and not constant
        -> each event is three doubles: Id_recording_device, neuronID, spiketimes

        -> 1D array to shape (x,3) where x is the number of events.
        -> this is decided by the nest I/O part, i.e. nest sends out events in 1D array
        """
        self.logger.info('MPI Internal : shared buffer : start create buffer')
        datasize = MPI.DOUBLE.Get_size()
        bufsize = 1000000 * 3  # NOTE: hardcoded (max.expected events per package from nest)
        self.logger.info(str(buffer_r_w))
        if buffer_r_w[1] == comm.Get_rank():  # creation of buffer only in the writing rank
            bufbytes = datasize * bufsize
        else:
            bufbytes = 0
        self.logger.info('MPI Internal : shared buffer : allocate buffer')
        win = MPI.Win.Allocate_shared(bufbytes, datasize, comm=comm)
        self.logger.info('MPI Internal : shared buffer : start shared buffer')
        buf, datasize = win.Shared_query(buffer_r_w[1])
        self.logger.info('MPI Internal : shared buffer : shared buffer')
        assert datasize == MPI.DOUBLE.Get_size()
        self.logger.info('MPI Internal : shared buffer : variable buffer')
        # create a numpy array (buffer) whose data points to the shared mem
        self.databuffer = np.ndarray(buffer=buf, dtype='d', shape=(bufsize,))
        self.logger.info('MPI Internal : shared buffer : end create buffer')

    # Management of internal writing buffer
    def ready_write_buffer(self):
        """
        wait that the buffer is ready to write
        """
        status_ = MPI.Status()
        # wait until ready to receive new data (i.e. the sender has cleared the buffer)
        self.logger.info("MPI Internal : write(ready) : buffer size wait ")
        if self.request_send_size_buffer is not None:
            self.timer.start(8)
            self.request_send_size_buffer.wait()
            self.timer.change(8, 9)
            self.logger.info(
                "MPI Internal : write(ready) : buffer receive :" + str(self.rank) + " from " + str(self.buffer_r_w[0]))
            request_buffer_read = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[0])
            self.logger.info("MPI Internal : write(ready) : buffer receive wait")
            self.send_spike_exit = not request_buffer_read.wait(status_)
            self.timer.stop(9)
        else:
            self.send_spike_exit = False
        self.shape_buffer = [0]  # head of the buffer, reset after each iteration
        self.logger.info("MPI Internal : write(ready) : buffer ready " + str(self.send_spike_exit))

    def end_writing(self):
        """
        send ending writing inside buffer
        """
        self.logger.info(
            "MPI Internal : write(end) : send size : " + str(np.sum(self.shape_buffer)) + " rank " + str(self.rank)
            + " to " + str(self.buffer_r_w[0]))
        self.request_send_size_buffer = MPI.COMM_WORLD.isend(self.shape_buffer, dest=self.buffer_r_w[0])
        self.logger.info("MPI Internal : write(end) : end")

    def release_write_buffer(self):
        """
        close connection with the sending
        """
        self.logger.info("MPI Internal : write(release) : end sim")
        status_ = MPI.Status()
        # wait until ready to receive new data (i.e. the sender has cleared the buffer)
        self.logger.info("MPI Internal : write(release) : wait size")
        self.timer.start(18)
        self.request_send_size_buffer.wait()
        self.timer.stop(18)
        self.logger.info("MPI Internal : write(release) : transmit end " + str(self.send_spike_exit))
        if not self.send_spike_exit:
            self.timer.start(18)
            req_buffer = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[0])
            self.logger.info("MPI Internal : write(release) : receive buffer accept")
            req_buffer.wait(status_)
            req_buffer = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[0])
            self.logger.info("MPI Internal : write(release) : send  end rank"
                             + str(self.rank) + " to " + str(self.buffer_r_w[1]))
            send_size = MPI.COMM_WORLD.isend(np.array([-1]), dest=self.buffer_r_w[0])
            send_size.wait(status_)
            self.timer.stop(18)
        self.logger.info("MPI Internal : write(release) : end")

    # Management of internal reading buffer
    def ready_to_read(self):
        """
        wait until it's ready to read the buffer
        """
        self.logger.info("MPI Internal : read(ready) : begin")
        status_ = MPI.Status()
        # wait until the receiver has cleared the buffer, i.e. filled with new data
        self.logger.info("MPI Internal : read(ready) : wait buffer ready ")
        if self.request_read_buffer is not None:
            self.timer.start(11)
            self.logger.info('MPI Internal : read(ready) : start read buffer: '
                             + str(self.rank) + " to " + str(self.buffer_r_w[1]))
            self.request_read_buffer.wait()
            self.timer.stop(11)
        self.timer.start(10)
        self.logger.info("MPI Internal : read(ready) : receive size : rank "
                         + str(self.rank) + " from " + str(self.buffer_r_w[1]))
        send_shape = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[1])
        self.logger.info("MPI Internal : read(ready) : receive size wait")
        res = send_shape.wait(status=status_)
        self.timer.stop(10)
        return res

    def end_read(self):
        """
        end to read the buffer
        """
        self.logger.info("MPI Internal : read(end) : end read buffer ")
        self.request_read_buffer = MPI.COMM_WORLD.isend(True, dest=self.buffer_r_w[1])
        self.logger.info("MPI Internal : read(end) : send end ")

    def release_read_buffer(self):
        """
        close connection with sender
        """
        self.logger.info("MPI Internal : read(release) : ending ")
        status_ = MPI.Status()
        self.timer.start(11)
        self.request_read_buffer.wait()
        self.timer.stop(11)
        # disconnect when everything is ending
        if self.shape_buffer[0] != -1:
            self.timer.start(12)
            self.logger.info("MPI Internal : read(release) : transmit end ")
            send_state = MPI.COMM_WORLD.irecv(source=self.buffer_r_w[1])
            self.logger.info("MPI Internal : read(release) : receive end ")
            send_state.wait(status=status_)
            req_buffer = MPI.COMM_WORLD.isend(False, dest=self.buffer_r_w[1])
            self.logger.info("MPI Internal : read(release) : send end ")
            req_buffer.wait()
            self.timer.stop(12)
        self.logger.info("MPI Internal : read(release) : end ")

    # Section 1 : spike trains exchange
    def send_spikes_ready(self):
        """
        see super class
        """
        self.logger.info("MPI Internal : spike(send) : ready send spikes")
        self.ready_write_buffer()

    def send_spikes(self):
        """
        see super class
        """
        self.logger.info("MPI Internal : spike(send) : spike send")
        self.end_writing()

    def send_spikes_trains(self, spike_trains):
        """
        see super class
        """
        self.logger.info('MPI Internal : spike(send) : begin')
        self.ready_write_buffer()
        self.logger.info('MPI Internal : spike(send) : buffer')
        if self.send_spike_exit:
            self.logger.info('MPI Internal : spike(send) : receive end ')
            return
        self.logger.info('MPI Internal : spike(send) : start spike_trains in buffer')
        #  create continue data with all spike trains
        self.timer.start(13)
        data_shape = []
        for index, spike_train in enumerate(spike_trains):
            data_shape.append(len(spike_train))
            # self.logger.info("TRS : spike times : "+str(index)+" " +str(len(spike_train))+
            #                  "\n"+str(spike_train))
        data = np.concatenate(spike_trains)
        self.shape_buffer = data_shape
        self.databuffer[:data.shape[0]] = data
        self.timer.stop(13)
        self.logger.info('MPI Internal : spike(send) : data write')
        self.end_writing()
        self.logger.info('MPI Internal : spike(send) : end')
        return

    def send_spikes_end(self):
        """
        see super class
        """
        self.logger.info("MPI Internal : spike(end) : end send")
        self.release_write_buffer()

    def get_spikes(self):
        """
        see super class
        """
        self.logger.info('MPI Internal : spike(get) : begin ')
        # wait until the data are ready to use
        self.shape_buffer = self.ready_to_read()
        self.logger.info('MPI Internal : spike(get) : receive end ' + str(np.sum(self.shape_buffer)))
        if self.shape_buffer[0] == -1:
            self.logger.info('MPI Internal : spike(get) : receive end ')
            return None
        return np.cumsum(np.insert(self.shape_buffer, 0, 0))

    def get_spikes_ready(self):
        """
        see super class
        """
        self.logger.info('MPI Internal : spike(ready) : ready get spikes')
        self.shape_buffer = self.ready_to_read()
        self.logger.info('MPI Internal : spike(ready) : ready to write : ' + str(np.sum(self.shape_buffer)))

    def get_spikes_release(self):
        """
        see super class
        """
        self.logger.info('MPI Internal : spike(release)')
        self.end_read()
        self.logger.info('MPI Internal : spike(release) : end')

    def get_spikes_end(self):
        """
        see super class
        """
        self.logger.info('MPI Internal : spike(end) : begin')
        self.release_read_buffer()
        self.logger.info('MPI Internal : spike(end) : end')

    # Section 2 : rate and time exchange
    def get_time_rate(self):
        """
        see super class
        """
        self.timer.start(15)
        self.logger.info("MPI Internal : rate(get) : get time rate")
        if self.request_send_done is not None:
            self.request_send_done.wait()
        self.logger.info("MPI Internal : rate(get) : rate :" + str(self.sender_rank))
        req_time = MPI.COMM_WORLD.irecv(source=self.sender_rank, tag=0)
        times = req_time.wait()
        self.timer.stop(15)
        if times[0] == -1e5:
            self.get_time_rate_exit = True
            self.logger.info("MPI Internal : rate(get) : times" + str(self.sender_rank))
            return times, None
        self.timer.start(16)
        req_data = MPI.COMM_WORLD.irecv(source=self.sender_rank, tag=1)
        self.logger.info("MPI Internal : rate(get) : data request")
        rate = req_data.wait()
        self.logger.info("MPI Internal : rate(get) : end")
        self.timer.stop(16)
        return times, rate

    def get_time_rate_release(self):
        """
        see super class
        """
        self.logger.info("MPI Internal : rate(release) : begin")
        self.request_send_done = MPI.COMM_WORLD.isend(True, dest=self.sender_rank)
        self.logger.info("MPI Internal : rate(release) : end")

    def get_time_rate_end(self):
        """
        see super class
        """
        self.logger.info("MPI Internal : rate(end) : wait time")
        if not self.get_time_rate_exit:
            self.request_send_done = MPI.COMM_WORLD.isend(False, dest=self.sender_rank)
        self.logger.info("MPI Internal : rate(end) : end ")

    def send_time_rate(self, time_step, rate):
        """
        see super class
        """
        self.logger.info("MPI Internal : rate(send) : init")
        if self.request_receive_time is not None:
            self.timer.start(17)
            self.logger.info("MPI Internal : rate(send) : wait request")
            self.request_receive_time.wait()
            self.request_receive_rate.wait()
            self.logger.info("MPI Internal : rate(send) : wait check")
            self.send_time_rate_exit = not self.request_read_done.wait()
            self.logger.info("MPI Internal : rate(send) : receive end " + str(self.send_time_rate_exit))
            self.timer.stop(17)
            if self.send_time_rate_exit:
                return
        # time of stating and ending step
        self.request_receive_time = MPI.COMM_WORLD.isend(time_step, dest=self.receiver_rank, tag=0)
        # send the size of the rate
        self.request_receive_rate = MPI.COMM_WORLD.isend(rate, dest=self.receiver_rank, tag=1)
        self.logger.info("MPI Internal : rate(send) : ask check")
        self.request_read_done = MPI.COMM_WORLD.irecv(source=self.receiver_rank)
        self.logger.info("MPI Internal : rate(send) : update buffer")

    def send_time_rate_end(self):
        """
        see super class
        """
        self.logger.info("MPI Internal : rate(end) : begin " + str(not self.send_time_rate_exit))
        if not self.send_time_rate_exit:
            self.request_receive_time = MPI.COMM_WORLD.isend([-1e5], dest=self.receiver_rank, tag=0)
        self.logger.info("MPI Internal : rate(end) : end")
