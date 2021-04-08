import numpy as np
import time
from nest_elephant_tvb.translation.communication.internal import CommunicationInternAbstract
from threading import Lock,BoundedSemaphore

final_barrier = BoundedSemaphore(2) # n-1 thread

# can be improve with condition and semaphore or event :  https://hackernoon.com/synchronization-primitives-in-python-564f89fee732


class Thread_communication(CommunicationInternAbstract):
    def __init__(self,logger=None,buffer_write_shape=None,buffer_write_type=np.float,buffer_write_status=0,
                 buffer_read=None,status_read=None,lock_read=None):
        super().__init__(logger=logger)
        if buffer_read is not None :
            self.buffer_read_data = buffer_read
            self.status_read = status_read
            self.lock_read = lock_read
        if buffer_write_shape is not None :
            self.logger.info('end MPI init')
            self.databuffer = np.empty(buffer_write_shape,dtype=buffer_write_type)
            self.buffer_write_data = [self.databuffer]
            self.status_write = [buffer_write_status]
            self.lock_write = Lock()
            self.shape_buffer = [0]
        self.logger.info('end MPI init')

    def finalise(self):
        self.logger.info('end MPI init')
        return not final_barrier.acquire(False)

    ## writter of the buffer
    def ready_write_buffer(self):
        self.logger.info('Thread : write buffer wait '+str(self.status_write[0][0]))
        while self.status_write[0][0] >= 0:
            # self.logger.info('Thread : statut '+str(self.status_write[0][0]))
            time.sleep(0.001)
            pass
        self.logger.info('Thread : write end buffer end wait '+str(self.shape_buffer))
        self.shape_buffer = [0]
        return self.status_write[0][0] == -1

    def end_writing(self):
        self.logger.info('Thread : end write wait '+str(self.status_write[0][0]) +" shape buffer "+str(self.shape_buffer))
        self.buffer_write_data[0]=self.databuffer
        with self.lock_write:
            if self.status_write[0][0] != -1:
                self.status_write[0] = self.shape_buffer
            else:
                self.logger('Thread : end ')
        self.logger.info('Thread : end write end '+str(self.status_write[0][0]))

    def release_write_buffer(self):
        self.logger.info('Thread : release write buffer '+str(self.status_write[0][0]))
        while self.status_write[0][0] >= 0:
            # self.logger.info('Thread : statut '+str(self.status_write[0][0]))
            time.sleep(0.001)
            pass
        with self.lock_write:
                self.status_write[0][0] = -1
        self.logger.info('Thread : release write buffer end '+str(self.status_write[0][0]))

    def ready_to_read(self):
        self.logger.info('Thread : ready read buffer wait '+str(self.status_read[0][0]))
        while self.status_read[0][0] == -2: # FAT END POINT
            # self.logger.info('Thread : statut '+str(self.status_read[0][0]))
            time.sleep(0.001)
            pass
        self.logger.info('Thread : ready read buffer end '+str(self.status_read[0][0]))
        self.databuffer = self.buffer_read_data[0]
        return self.status_read[0]

    def end_read(self):
        self.logger.info('Thread : end read buffer '+str(self.status_read[0][0]))
        with self.lock_read:
            if self.status_read[0][0] != -1:
                self.status_read[0][0] = -2
        self.logger.info('Thread : end read buffer end '+str(self.status_read[0][0]))

    def release_read_buffer(self):
        self.logger.info('Thread : release read buffer '+str(self.status_read[0][0]))
        while self.status_read[0][0] == -2: # FAT END POINT
            # self.logger.info('Thread : statut '+str(self.status_read[0][0]))
            time.sleep(0.001)
            pass
        with self.lock_read:
            self.status_read[0][0] = -1
        self.logger.info('Thread : release read buffer unlock '+str(self.status_read[0][0]))


    def send_spikes_ready(self):
        self.logger.info(" Thread : ready send spikes")
        self.send_spike_exit = self.ready_write_buffer()

    def send_spikes(self):
        self.logger.info(" Thread : spike send")
        self.end_writing()

    def send_spikes_trains(self,spike_trains):
        self.logger.info('Thread : spike(send) : begin')
        self.send_spike_exit = self.ready_write_buffer()
        self.logger.info('Thread : spike(send) : buffer')
        if self.send_spike_exit:
            self.logger.info('Thread : spike(get) : receive end ')
            return
        data_shape = []
        for index, spike_train in enumerate(spike_trains):
            data_shape.append(len(spike_train))
            # self.logger.info("TRS : spike times : "+str(index)+" " +str(len(spike_train))+
            #                  "\n"+str(spike_train))
        self.logger.info('Thread : spike(send) : '+str(np.concatenate(spike_trains)))
        data = np.concatenate(spike_trains)
        self.logger.info('Thread : spike(send) : '+str(data.shape))
        self.shape_buffer = data_shape
        if len(data) !=0:
            self.databuffer[:data.shape[0]] = data
        self.logger.info('Thread : spike(send) : data write')
        self.end_writing()
        self.logger.info('Thread : spike(send) : end')


    def send_spikes_end(self):
        self.logger.info("Thread : end send")
        self.release_write_buffer()

    def get_spikes(self):
        self.logger.info('Thread : spike(get) : begin ')
        # wait until the data are ready to use
        self.shape_buffer = self.ready_to_read()
        self.logger.info('Thread : spike(get) : receive end '+str(self.shape_buffer))
        if self.shape_buffer[0] == -1:
            self.logger.info('Thread : spike(get) : receive end ')
            return None
        self.logger.info('Thread : spike(get) : reshape data')
        spikes_times = []
        index = 0
        for nb_spike in self.shape_buffer:
            self.logger.info("nb spike shape :" +str(index))
            spikes_times.append(self.databuffer[index:index + int(nb_spike)])
            index += int(nb_spike)
        self.logger.info('Thread : spike(get) : end reshape data')
        return spikes_times

    def get_spikes_ready(self):
        self.logger.info('Thread : spike(ready) : ready get spikes')
        self.shape_buffer = self.ready_to_read()
        self.logger.info('Thread : spike(ready) : ready to write : ' + str(self.shape_buffer))

    def get_spikes_release(self):
        self.logger.info('Thread : spike(release)')
        self.end_read()
        self.logger.info('Thread : spike(get) : end')

    def get_spikes_end(self):
        self.logger.info('Thread : spike(end) : begin')
        self.release_read_buffer()
        self.logger.info('Thread : spike(end) : end')

    def get_time_rate(self):
        self.logger.info("Thread : rate(get) : get time rate")
        self.shape_buffer = self.ready_to_read()
        if self.shape_buffer[0] == -1:
            self.logger.info("Thread : rate(get) : get exit")
            self.get_time_rate_exit = True
            return [self.shape_buffer], None
        times = self.buffer_read_data[0][0]
        self.logger.info("Thread : rate(get) : data request")
        rate = self.buffer_read_data[0][1]
        self.logger.info("Thread : rate(get) : end")
        return times,rate

    def get_time_rate_release(self):
        self.logger.info('Thread : rate(release)')
        self.end_read()
        self.logger.info('Thread : time(get) : end')

    def get_time_rate_end(self):
        self.logger.info('Thread : spike(end) : begin')
        self.release_read_buffer()
        self.logger.info('Thread : spike(end) : end')

    def send_time_rate(self, time_step, rate):
        self.logger.info('Thread : spike(send) : begin')
        self.send_time_rate_exit = self.ready_write_buffer()
        self.logger.info('Thread : spike(send) : buffer')
        if self.send_time_rate_exit:
            self.logger.info('Thread : spike(get) : receive end ')
            return
        self.shape_buffer = [time_step.shape[0]]
        self.logger.info('Thread : spike(send) : time :'+str(time_step))
        self.logger.info('Thread : spike(send) : buffer :'+str(np.array(self.databuffer).shape))
        self.databuffer = [time_step,rate]
        self.logger.info('Thread : spike(send) : data write')
        self.end_writing()
        self.logger.info('Thread : spike(send) : end')

    def send_time_rate_end(self):
        self.logger.info("Thread : rate(end) : begin "+str( not self.send_time_rate_exit))
        if not self.send_time_rate_exit:
            self.release_write_buffer()
        self.logger.info("Thread : rate(end) : end")