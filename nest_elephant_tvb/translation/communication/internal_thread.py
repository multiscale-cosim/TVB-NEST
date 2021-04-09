#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
import time
from threading import Lock, BoundedSemaphore
from nest_elephant_tvb.translation.communication.internal import CommunicationInternAbstract

_final_barrier = BoundedSemaphore(2)  # n-1 thread # improvement be include in the class


class Thread_communication(CommunicationInternAbstract):
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
                 buffer_read=None, status_read=None, lock_read=None):
        super().__init__(logger=logger)
        # set variable if reading buffer is used
        if buffer_read is not None and status_read is not None and lock_read is not None:
            self.logger.info('end MPI init')
            self.buffer_read_data = buffer_read  # variable contains reading buffer
            self.status_read = status_read       # status of read buffer and it can contain the dimension of the data
            self.lock_read = lock_read           # lock for write in the status
        elif buffer_read is not None or status_read is not None or lock_read is not None:
            raise Exception('missing parameter for using reading buffer')
        # set variable if writing buffer is used
        if buffer_write_shape is not None and buffer_write_status is not None:
            self.logger.info('end MPI init')
            self.databuffer = np.empty(buffer_write_shape, dtype=buffer_write_type)  # create buffer
            self.buffer_write_data = [self.databuffer]  # variable for shared buffer
            self.status_write = [buffer_write_status]   # status of buffer and contains the dimension of the data
            self.lock_write = Lock()                    # lock for write in the status
            self.shape_buffer = [0]                     # dimension of the data
        elif buffer_write_shape is not None or buffer_write_status is not None:
            raise Exception('missing parameter for using writing buffer')
        self.logger.info('end MPI init')

    def finalise(self):
        """
        Synchronize thread before the end of the MPI
        :return True if it's the last one to pass
        """
        self.logger.info('end MPI init')
        return not _final_barrier.acquire(False)

    # Management of internal writing buffer
    def ready_write_buffer(self):
        """
        wait until it's ready to write in the buffer
        :return if the communication is ending
        """
        self.logger.info('Thread : write buffer wait '+str(self.status_write[0][0]))
        while self.status_write[0][0] >= 0:  # wait to write
            time.sleep(0.001)
        self.logger.info('Thread : write end buffer end wait '+str(self.shape_buffer))
        self.shape_buffer = [0]  # reinitialise the buffer shape
        return self.status_write[0][0] == -1

    def end_write_buffer(self):
        """
        end to write in the buffer
        """
        self.logger.info('Thread : end write wait '+str(self.status_write[0][0])
                         + " shape buffer "+str(self.shape_buffer))
        self.buffer_write_data[0] = self.databuffer  # pass the buffer in the shared variable
        with self.lock_write:
            if self.status_write[0][0] != -1:
                self.status_write[0] = self.shape_buffer  # pass the dimension of the buffer
            else:
                self.logger('Thread : end ')
        self.logger.info('Thread : end write end '+str(self.status_write[0][0]))

    def release_write_buffer(self):
        """
        release writing buffer and send the end of the communication
        """
        self.logger.info('Thread : release write buffer '+str(self.status_write[0][0]))
        while self.status_write[0][0] >= 0:  # wait before change the buffer
            time.sleep(0.001)
        with self.lock_write:
            self.status_write[0][0] = -1  # Close connection
        self.logger.info('Thread : release write buffer end '+str(self.status_write[0][0]))

    # Management of internal reading buffer
    def ready_to_read(self):
        """
        wait until it's ready to read in the buffer
        :return: if the communication is ending
        """
        self.logger.info('Thread : ready read buffer wait '+str(self.status_read[0][0]))
        while self.status_read[0][0] == -2:  # wait the end of reading buffer
            time.sleep(0.001)
        self.logger.info('Thread : ready read buffer end '+str(self.status_read[0][0]))
        self.databuffer = self.buffer_read_data[0]  # write in the buffer
        return self.status_read[0]  # return status

    def end_read(self):
        """
        end to read in the buffer
        """
        self.logger.info('Thread : end read buffer '+str(self.status_read[0][0]))
        with self.lock_read:
            if self.status_read[0][0] != -1:
                self.status_read[0][0] = -2  # end the reading of the buffer
        self.logger.info('Thread : end read buffer end '+str(self.status_read[0][0]))

    def release_read_buffer(self):
        """
        release reading buffer and send the end of the communication
        """
        self.logger.info('Thread : release read buffer '+str(self.status_read[0][0]))
        while self.status_read[0][0] == -2:  # wait until the written is ending
            time.sleep(0.001)
        with self.lock_read:
            self.status_read[0][0] = -1  # close the connection
        self.logger.info('Thread : release read buffer unlock '+str(self.status_read[0][0]))

    # Section 1 : spike trains exchange
    def send_spikes_ready(self):
        """
        see super class
        """
        self.logger.info(" Thread : ready send spikes")
        self.send_spike_exit = self.ready_write_buffer()

    def send_spikes(self):
        """
        see super class
        """
        self.logger.info(" Thread : spike send")
        self.end_write_buffer()

    def send_spikes_trains(self, spike_trains):
        """
        see super class
        """
        self.logger.info('Thread : spike(send) : begin')
        self.send_spike_exit = self.ready_write_buffer()
        self.logger.info('Thread : spike(send) : buffer')
        if self.send_spike_exit:
            self.logger.info('Thread : spike(get) : receive end ')
            return
        # create continue data with all spike trains
        data_shape = []
        for index, spike_train in enumerate(spike_trains):
            data_shape.append(len(spike_train))
            # self.logger.info("TRS : spike times : "+str(index)+" " +str(len(spike_train))+
            #                  "\n"+str(spike_train))
        data = np.concatenate(spike_trains)
        self.shape_buffer = data_shape
        # special case for empty data
        if len(data) != 0:
            self.databuffer[:data.shape[0]] = data
        self.logger.info('Thread : spike(send) : data write')
        self.end_write_buffer()
        self.logger.info('Thread : spike(send) : end')

    def send_spikes_end(self):
        """
        see super class
        """
        self.logger.info("Thread : end send")
        self.release_write_buffer()

    def get_spikes(self):
        """
        see super class
        """
        self.logger.info('Thread : spike(get) : begin ')
        # wait until the data are ready to use
        self.shape_buffer = self.ready_to_read()
        self.logger.info('Thread : spike(get) : receive end '+str(self.shape_buffer))
        if self.shape_buffer[0] == -1:
            self.logger.info('Thread : spike(get) : receive end ')
            return None
        self.logger.info('Thread : spike(get) : reshape data')
        # reshape the data for use by the communicator with the simulator
        spikes_times = []
        index = 0
        for nb_spike in self.shape_buffer:
            self.logger.info("nb spike shape :" + str(index))
            spikes_times.append(self.databuffer[index:index + int(nb_spike)])
            index += int(nb_spike)
        self.logger.info('Thread : spike(get) : end reshape data')
        return spikes_times

    def get_spikes_ready(self):
        """
        see super class
        """
        self.logger.info('Thread : spike(ready) : ready get spikes')
        self.shape_buffer = self.ready_to_read()
        self.logger.info('Thread : spike(ready) : ready to write : ' + str(self.shape_buffer))

    def get_spikes_release(self):
        """
        see super class
        """
        self.logger.info('Thread : spike(release)')
        self.end_read()
        self.logger.info('Thread : spike(get) : end')

    def get_spikes_end(self):
        """
        see super class
        """
        self.logger.info('Thread : spike(end) : begin')
        self.release_read_buffer()
        self.logger.info('Thread : spike(end) : end')

    def get_time_rate(self):
        """
        see super class
        """
        self.logger.info("Thread : rate(get) : get time rate")
        self.shape_buffer = self.ready_to_read()
        if self.shape_buffer[0] == -1:
            self.logger.info("Thread : rate(get) : get exit")
            self.get_time_rate_exit = True
            return [self.shape_buffer], None
        times = self.buffer_read_data[0][0]
        self.logger.info("Thread : rate(get) : data request : time :"+str(times))
        rate = self.buffer_read_data[0][1]
        self.logger.info("Thread : rate(get) : end")
        return times, rate

    def get_time_rate_release(self):
        """
        see super class
        """
        self.logger.info('Thread : rate(release)')
        self.end_read()
        self.logger.info('Thread : time(get) : end')

    def get_time_rate_end(self):
        """
        see super class
        """
        self.logger.info('Thread : spike(end) : begin')
        self.release_read_buffer()
        self.logger.info('Thread : spike(end) : end')

    def send_time_rate(self, time_step, rate):
        """
        see super class
        """
        self.logger.info('Thread : spike(send) : begin')
        self.send_time_rate_exit = self.ready_write_buffer()
        self.logger.info('Thread : spike(send) : buffer')
        if self.send_time_rate_exit:
            self.logger.info('Thread : spike(get) : receive end ')
            return
        self.shape_buffer = [time_step.shape[0]]
        self.logger.info('Thread : spike(send) : time :'+str(time_step))
        self.logger.info('Thread : spike(send) : buffer :'+str(np.array(self.databuffer).shape))
        self.databuffer = [time_step, rate]
        self.logger.info('Thread : spike(send) : data write')
        self.end_write_buffer()
        self.logger.info('Thread : spike(send) : end')

    def send_time_rate_end(self):
        """
        see super class
        """
        self.logger.info("Thread : rate(end) : begin "+str(not self.send_time_rate_exit))
        if not self.send_time_rate_exit:
            self.release_write_buffer()
        self.logger.info("Thread : rate(end) : end")
