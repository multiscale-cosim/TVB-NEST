#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
import time
from threading import Lock, BoundedSemaphore
from nest_elephant_tvb.transformation.communication.internal import CommunicationInternAbstract

_final_barrier = BoundedSemaphore(2)  # n-1 thread # improvement be include in the class


class ThreadCommunication(CommunicationInternAbstract):
    """
    Class for using thread for the internal communication

    state of the status:
        >= 0 : shape of the buffer
        -1 : close connection
        -2 : end to read buffer
    """

    # can be improve with condition and semaphore or event :
    # https://hackernoon.com/synchronization-primitives-in-python-564f89fee732

    def __init__(self, logger=None,
                 buffer_write_shape=None, buffer_write_type=np.float, buffer_write_status=None,
                 buffer_read=None, status_read=None, lock_read=None, timer=None):
        """
        initialisation of the thread
        :param logger: logger for the communication
        :param buffer_write_shape: shape of the buffer
        :param buffer_write_type: datatype of buffer
        :param buffer_write_status: initialisation of the status of buffer
        :param buffer_read: variable of the shared writing buffer
        :param status_read: status of a writing buffer
        :param lock_read: locker of a writing buffer
        """
        super().__init__(logger=logger, timer=timer)
        # set variable if reading buffer is used
        if buffer_read is not None and status_read is not None and lock_read is not None:
            self.logger.info('Thread Internal : read buffer')
            self.buffer_read_data = buffer_read  # variable contains reading buffer
            self.status_read = status_read  # status of read buffer and it can contain the dimension of the data
            self.lock_read = lock_read  # lock for write in the status
        elif buffer_read is not None or status_read is not None or lock_read is not None:
            raise Exception('Thread Internal : missing parameter for using reading buffer')
        # set variable if writing buffer is used
        if buffer_write_shape is not None and buffer_write_status is not None:
            self.logger.info('Thread Internal : write buffer')
            self.databuffer = np.empty(buffer_write_shape, dtype=buffer_write_type)  # create buffer
            self.buffer_write_data = [self.databuffer]  # variable for shared buffer
            self.status_write = [buffer_write_status]  # status of buffer and contains the dimension of the data
            self.lock_write = Lock()  # lock for write in the status
            self.shape_buffer = [0]  # dimension of the data
        elif buffer_write_shape is not None or buffer_write_status is not None:
            raise Exception('missing parameter for using writing buffer')
        self.logger.info('Thread Internal : end Thread init')

    def finalise(self):
        """
        Synchronize thread before the end of the MPI
        :return True if it's the last one to pass
        """
        self.logger.info('Thread Internal : finalize')
        return not _final_barrier.acquire(False)

    # Management of internal writing buffer
    def ready_write_buffer(self):
        """
        wait until it's ready to write in the buffer
        :return if the communication is ending
        """
        self.logger.info('Thread Internal : write(ready) : wait ' + str(self.status_write[0][0]))
        self.timer.start(8)
        while self.status_write[0][0] >= 0:  # wait to write
            time.sleep(0.001)
        self.timer.stop(8)
        self.logger.info('Thread Internal : write(ready) : end wait ' + str(self.shape_buffer))
        self.shape_buffer = [0]  # reinitialise the buffer shape
        return self.status_write[0][0] == -1

    def end_write_buffer(self):
        """
        end to write in the buffer
        """
        self.logger.info('Thread Internal : write(end) : begin')
        self.buffer_write_data[0] = self.databuffer  # pass the buffer in the shared variable
        self.timer.start(9)
        with self.lock_write:
            if self.status_write[0][0] != -1:
                self.status_write[0] = self.shape_buffer  # pass the dimension of the buffer
            else:
                self.logger('Thread Internal : write(end) : finish')
        self.timer.stop(9)
        self.logger.info('Thread Internal : write(end) : end')

    def release_write_buffer(self):
        """
        release writing buffer and send the end of the communication
        """
        self.logger.info('Thread Internal : write(release) : write buffer ' + str(self.status_write[0][0]))
        self.timer.start(10)
        while self.status_write[0][0] >= 0:  # wait before change the buffer
            time.sleep(0.001)
        with self.lock_write:
            self.status_write[0][0] = -1  # Close connection
        self.timer.stop(10)
        self.logger.info('Thread Internal : write(release) : write buffer end ' + str(self.status_write[0][0]))

    # Management of internal reading buffer
    def ready_to_read(self):
        """
        wait until it's ready to read in the buffer
        :return: if the communication is ending
        """
        self.logger.info('Thread Internal : read(ready) : buffer wait ' + str(self.status_read[0][0]))
        self.timer.start(11)
        while self.status_read[0][0] == -2:  # wait the end of reading buffer
            time.sleep(0.001)
        self.timer.stop(11)
        self.logger.info('Thread Internal : read(ready) : buffer end ' + str(self.status_read[0][0]))
        self.databuffer = self.buffer_read_data[0]  # write in the buffer
        return self.status_read[0]  # return status

    def end_read(self):
        """
        end to read in the buffer
        """
        self.logger.info('Thread Internal : read(end) : begin ' + str(self.status_read[0][0]))
        self.timer.start(12)
        with self.lock_read:
            if self.status_read[0][0] != -1:
                self.status_read[0][0] = -2  # end the reading of the buffer
        self.timer.stop(12)
        self.logger.info('Thread Internal : read(end) : buffer end ' + str(self.status_read[0][0]))

    def release_read_buffer(self):
        """
        release reading buffer and send the end of the communication
        """
        self.logger.info('Thread Internal : read(release): buffer ' + str(self.status_read[0][0]))
        self.timer.start(13)
        while self.status_read[0][0] == -2:  # wait until the written is ending
            time.sleep(0.001)
        with self.lock_read:
            self.status_read[0][0] = -1  # close the connection
        self.timer.stop(13)
        self.logger.info('Thread Internal : read(release): read buffer unlock ' + str(self.status_read[0][0]))

    # Section 1 : spike trains exchange
    def send_spikes_ready(self):
        """
        see super class
        """
        self.logger.info(" Thread Internal : spike(send) : ready send spikes")
        self.send_spike_exit = self.ready_write_buffer()

    def send_spikes(self):
        """
        see super class
        """
        self.logger.info(" Thread Internal : spike(send) : spike send")
        self.end_write_buffer()

    def send_spikes_trains(self, spike_trains):
        """
        see super class
        """
        self.logger.info('Thread Internal : spike(send) : begin')
        self.send_spike_exit = self.ready_write_buffer()
        self.logger.info('Thread Internal : spike(send) : buffer')
        if self.send_spike_exit:
            self.logger.info('Thread Internal : spike(send) : receive end ')
            return
        # create continue data with all spike trains
        self.timer.start(14)
        data_shape = []
        for index, spike_train in enumerate(spike_trains):
            data_shape.append(len(spike_train))
            # self.logger.info("TRS : spike times : "+str(index)+" " +str(len(spike_train))+
            #                  "\n"+str(spike_train))
        data = np.concatenate(spike_trains)
        self.shape_buffer = data_shape
        self.timer.stop(14)
        # special case for empty data
        if len(data) != 0:
            self.databuffer[:data.shape[0]] = data
        self.logger.info('Thread Internal : spike(send) : data write')
        self.end_write_buffer()
        self.logger.info('Thread Internal : spike(send) : end')

    def send_spikes_end(self):
        """
        see super class
        """
        self.logger.info("Thread Internal : spike(end) : end send")
        self.release_write_buffer()

    def get_spikes(self):
        """
        see super class
        """
        self.logger.info('Thread Internal : spike(get) : begin ')
        # wait until the data are ready to use
        self.shape_buffer = self.ready_to_read()
        self.logger.info('Thread Internal : spike(get) : receive end ' + str(self.shape_buffer))
        if self.shape_buffer[0] == -1:
            self.logger.info('Thread Internal : spike(get) : receive end ')
            return None
        return np.cumsum(np.insert(self.shape_buffer, 0, 0))

    def get_spikes_ready(self):
        """
        see super class
        """
        self.logger.info('Thread Internal : spike(ready) : ready get spikes')
        self.shape_buffer = self.ready_to_read()
        self.logger.info('Thread Internal : spike(ready) : ready to write : ' + str(self.shape_buffer))

    def get_spikes_release(self):
        """
        see super class
        """
        self.logger.info('Thread Internal : spike(release)')
        self.end_read()
        self.logger.info('Thread Internal : spike(release) : end')

    def get_spikes_end(self):
        """
        see super class
        """
        self.logger.info('Thread Internal : spike(end) : begin')
        self.release_read_buffer()
        self.logger.info('Thread Internal : spike(end) : end')

    # Section 2 : rate and time exchange
    def get_time_rate(self):
        """
        see super class
        """
        self.logger.info("Thread Internal : rate(get) : get time rate")
        self.shape_buffer = self.ready_to_read()
        if self.shape_buffer[0] == -1:
            self.logger.info("Thread Internal : rate(get) : get exit")
            self.get_time_rate_exit = True
            return [self.shape_buffer], None
        times = self.buffer_read_data[0][0]
        self.logger.info("Thread Internal : rate(get) : data request : time :" + str(times))
        rate = self.buffer_read_data[0][1]
        self.logger.info("Thread Internal : rate(get) : end")
        return times, rate

    def get_time_rate_release(self):
        """
        see super class
        """
        self.logger.info('Thread Internal : rate(release)')
        self.end_read()
        self.logger.info('Thread Internal : rate(release) : end')

    def get_time_rate_end(self):
        """
        see super class
        """
        self.logger.info('Thread Internal : rate(end) : begin')
        self.release_read_buffer()
        self.logger.info('Thread Internal : rate(end) : end')

    def send_time_rate(self, time_step, rate):
        """
        see super class
        """
        self.logger.info('Thread Internal : rate(send) : begin')
        self.send_time_rate_exit = self.ready_write_buffer()
        self.logger.info('Thread Internal : rate(send) : buffer')
        if self.send_time_rate_exit:
            self.logger.info('Thread Internal : rate(get) : receive end ')
            return
        self.shape_buffer = [time_step.shape[0]]
        self.logger.info('Thread Internal : rate(send) : time :' + str(time_step))
        self.logger.info('Thread Internal : rate(send) : buffer :' + str(np.array(self.databuffer).shape))
        self.databuffer = [time_step, rate]
        self.logger.info('Thread Internal : rate(send) : data write')
        self.end_write_buffer()
        self.logger.info('Thread Internal : rate(send) : end')

    def send_time_rate_end(self):
        """
        see super class
        """
        self.logger.info("Thread Internal : rate(end) : begin " + str(not self.send_time_rate_exit))
        if not self.send_time_rate_exit:
            self.release_write_buffer()
        self.logger.info("Thread Internal : rate(end) : end")
