from mpi4py import MPI
from nest_elephant_tvb.translation.mpi.mpi_translator import MPI_communication
import numpy as np

class Receiver_Nest_Data(MPI_communication):
    def ready_to_send_spikes(self):
        self.logger.info(" Receiver Nest : ready send spikes")
        self.ready_write_buffer()
        return self.accept_buffer

    def send_spikes(self):
        self.logger.info(" Receiver Nest : spike send")
        self.end_writing()

    def end_send_spikes(self):
        self.logger.info(" Receiver Nest : end send")
        self.release_write_buffer()

    # See todo in the beginning, encapsulate I/O, transformer, science parts
    def simulation_time(self):
        '''
        Receive data on rank 0. Put it into the shared mem buffer.
        Replaces the former 'receive' function.
        NOTE: First refactored version -> not pretty, not final.
        '''
        self.logger.info(" Receiver Nest : simulation time")
        status_ = MPI.Status()
        num_sending = self.port_comm.Get_remote_size()  # how many NEST ranks are sending?
        # TODO: It seems the 'check' variable is used to receive tags from NEST, i.e. ready for send...
        # change this in the future, also mentioned in the FatEndPoint solution from Wouter.
        check = np.empty(1, dtype='b')
        shape = np.empty(1, dtype='i')
        count = 0
        # TODO: the last two buffer entries are used for shared information
        # --> they replace the status_data variable from previous version
        # --> find more elegant solution?
        while (True):
            self.logger.info(" Receiver Nest : loop start : wait all")

            # TODO: This is still not correct. We only check for the Tag of the last rank.
            # TODO: IF all ranks send always the same tag in one iteration (simulation step)
            # TODO: then this works. But it should be handled differently!!!!
            for i in range(num_sending):
                # new: We do not care which source sends first, give MPI the freedom to send in whichever order.
                self.port_comm.Recv([check, 1, MPI.CXX_BOOL], source=i, tag=MPI.ANY_TAG, status=status_)
            # TODO: handle properly, all ranks send tag 0?
            if status_.Get_tag() == 0:
                # ready to write in the buffer
                self.logger.info(" Receiver Nest : prepare buffer")
                ready = self.ready_to_send_spikes()
                if not ready:
                    break

                self.logger.info(" Receiver Nest : start get data")
                for source in range(num_sending):
                    # send 'ready' to the nest rank
                    self.port_comm.Send([np.array(True, dtype='b'), MPI.BOOL], dest=source, tag=0)
                    # receive package size info
                    self.port_comm.Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                    # NEW: receive directly into the buffer
                    self.port_comm.Recv([self.databuffer[self.size_buffer:], MPI.DOUBLE], source=source, tag=0, status=status_)
                    self.size_buffer += shape[0]  # move head
                    # TODO: revisit and check for proper encapsulation
                    # Here, storing and adding the spikes to the histogram was done
                    # Old code: store.add_spikes(count,data)
                    # This increased the workload of this MPI rank.
                    # All science and analysis stuff is moved to the 'sender' part. Because future parallel.
                self.logger.info(" Receiver Nest : end receive data")
                self.send_spikes()

            # TODO: handle properly, all ranks send tag 1?
            elif status_.Get_tag() == 1:
                count += 1
                self.logger.info("Receiver Nest : receive end " + str(count))
            # TODO: handle properly, all ranks send tag 2?
            elif status_.Get_tag() == 2:
                self.logger.info("Receiver Nest : end simulation")
                self.end_send_spikes()
                break
            else:
                raise Exception("bad mpi tag" + str(status_.Get_tag()))
        self.logger.info('Receiver Nest : End of receive function')

class Send_Data_to_Nest(MPI_communication):
    def __init__(self,id_first_spike_detector,sender_rank,*arg,**karg):
        super().__init__(*arg,**karg)
        self.logger.info('Send Nest : init')
        self.id_first_spike_detector = id_first_spike_detector
        self.logger.info('Send Nest : end init')
        self.shape_buffer = None

    def get_spikes(self):
        self.logger.info('Send Nest : spike(get) : begin ')
        # wait until the data are ready to use
        self.shape_buffer = self.ready_to_read()
        if self.shape_buffer[0] == -1:
            self.logger.info('Send Nest : spike(get) : receive end ')
            return None
        self.logger.info('Send Nest : spike(get) : reshape data')
        spikes_times = []
        index = 0
        for nb_spike in self.shape_buffer:
            self.logger.info(index)
            spikes_times.append(self.databuffer[index:index + int(nb_spike)])
            index += int(nb_spike)
        self.logger.info('Send Nest : spike(get) : end reshape data')
        self.end_read()
        self.logger.info('Send Nest : spike(get) : end')
        return spikes_times

    def release_get_spikes(self):
        self.logger.info('Send Nest : spike(release)')
        pass

    def end_get_spikes(self):
        self.logger.info('Send Nest : spike(end) : begin')
        self.release_read_buffer(self.shape_buffer)
        self.logger.info('Send Nest : spike(end) : end')

    # See todo in the beginning, encapsulate I/O, transformer, science parts
    def simulation_time(self):
        '''
        the sending part of the translator
        :param logger : logger
        :param nb_spike_generator: the number of spike generator
        :param status_data: the status of the buffer (SHARED between thread)
        :param buffer_spike: the buffer which contains the data (SHARED between thread)
        :return:
        '''
        self.logger.info('Send Nest : simulation')
        # initialisation variable before the loop
        status_ = MPI.Status()
        source_sending = np.arange(0,self.port_comm.Get_remote_size(),1) # list of all the process for the communication
        check = np.empty(1,dtype='b')
        while True: # FAT END POINT
            self.logger.info('Send Nest : loop start')
            for source in source_sending:
                self.port_comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
            self.logger.info("Send Nest : Get check : status : " +str(status_.Get_tag()))
            if status_.Get_tag() == 0:
                self.logger.info("Send Nest : start to send ")
                spikes_times = self.get_spikes()
                self.logger.info("Send Nest : shape buffer "+str(self.shape_buffer[0]))
                if self.shape_buffer[0] == -1:
                    break
                self.logger.info("Send Nest : spike time")
                # Waiting for some processus ask for receive the spikes
                for source in source_sending:
                    # receive list ids
                    size_list = np.empty(1, dtype='i')
                    self.port_comm.Recv([size_list, 1, MPI.INT], source=source, tag=0, status=status_)
                    if size_list[0] != 0:
                        list_id = np.empty(size_list, dtype='i')
                        self.port_comm.Recv([list_id, size_list, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
                        # Select the good spike train and send it
                        # logger.info(" TVB to Nest:"+str(data))
                        self.logger.info("Send Nest : rank "+str(source)+" list_id "+str(list_id))
                        data = []
                        shape = []
                        for i in list_id:
                            shape += [spikes_times[i-self.id_first_spike_detector].shape[0]]
                            data += [spikes_times[i-self.id_first_spike_detector]]
                        send_shape = np.array(np.concatenate(([np.sum(shape)],shape)), dtype='i')
                        # firstly send the size of the spikes train
                        self.port_comm.Send([send_shape, MPI.INT], dest=status_.Get_source(), tag=list_id[0])
                        # secondly send the spikes train
                        data = np.concatenate(data).astype('d')
                        self.port_comm.Send([data, MPI.DOUBLE], dest=source, tag=list_id[0])
                self.logger.info("Send Nest : end receive data")
                self.release_get_spikes()
                self.logger.info("Send Nest : end sending")
            elif  status_.Get_tag() == 1:
                # ending the update of the all the spike train from one processus
                self.logger.info("Send Nest : end run ")
            elif status_.Get_tag() == 2:
                self.logger.info("Send Nest : end simulation ")
                self.end_get_spikes()
                self.logger.info("Send Nest : send false ")
                break
            else:
                raise Exception("bad mpi tag : "+str(status_.Get_tag()))