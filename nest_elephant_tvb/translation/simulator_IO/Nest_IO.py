#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import numpy as np
from nest_elephant_tvb.translation.communication.mpi_io_external import MPI_communication_extern


class Receiver_Nest_Data(MPI_communication_extern):
    """
    Class for the receiving data from Nest and transfer them to the translation function process.
    """

    def simulation_time(self):
        """
        Receive data from Nest and add them in a shared buffer.
        """
        self.logger.info("Receiver Nest : simulation time")
        status_ = MPI.Status()
        num_sending = self.port_comms[0].Get_remote_size()  # The total number of the rank in Nest MPI_COMM_WORLD
        check = np.empty(1, dtype='b')  # variable to get the state of Nest
        shape = np.empty(1, dtype='i')  # variable to receive the shape of the data
        count = 0  # count the number of run
        while True:
            self.logger.info("Receiver Nest : loop start : wait all")
            self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
            state_nest = status_.Get_tag()
            for source in range(1, num_sending):
                # improvement: We do not care which source sends first, give MPI the freedom to send in whichever order.
                self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
                if state_nest != status_.Get_tag():
                    raise Exception('Abnormal state : the state of Nest is different between rank')

            if status_.Get_tag() == 0:
                # INTERNAL :ready to write in the buffer
                self.logger.info("Receiver Nest : prepare buffer")
                self.communication_internal.send_spikes_ready()
                if self.communication_internal.send_spike_exit:
                    self.logger.info("Receiver Nest : break")
                    break

                self.logger.info("Receiver Nest : start get data")
                for source in range(num_sending):
                    # send 'ready' to the nest rank
                    self.port_comms[0].Send([np.array(True, dtype='b'), MPI.BOOL], dest=source, tag=0)
                    # receive package size info
                    self.port_comms[0].Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                    self.logger.info("Receiver Nest : shape : "+str(self.communication_internal.shape_buffer))
                    # Add data in the buffer
                    self.port_comms[0].Recv([self.communication_internal.databuffer[self.communication_internal.shape_buffer[0]:], MPI.DOUBLE],
                                        source=source, tag=0, status=status_)
                    self.communication_internal.shape_buffer[0] += shape[0]  # move head
                self.logger.info("Receiver Nest : end receive data")

                # INTERNAL : end to write in the buffer
                self.communication_internal.send_spikes()

            elif status_.Get_tag() == 1:
                count += 1
                self.logger.info("Receiver Nest : receive end " + str(count))

            elif status_.Get_tag() == 2:
                self.logger.info("Receiver Nest : end simulation")
                # INTERNAL : close the communication
                self.communication_internal.send_spikes_end()
                break

            else:
                raise Exception("Abnormal tag : bad mpi tag" + str(status_.Get_tag()))

        self.logger.info('Receiver Nest : End of receive function')


class Send_Data_to_Nest(MPI_communication_extern):
    """
    Class for sending data to Nest. The data are from the translated function.
    """

    def __init__(self, id_first_spike_detector, *arg, **karg):
        super().__init__(*arg, **karg)
        self.id_first_spike_detector = id_first_spike_detector
        self.logger.info('Send Nest : end init')

    def simulation_time(self):
        """
        Send data to Nest from a shared buffer
        """
        self.logger.info('Send Nest : simulation')
        # initialisation variable before the loop
        status_ = MPI.Status()
        source_sending = np.arange(0, self.port_comms[0].Get_remote_size(), 1)  # list of all the rank of Nest MPI_COMM_WORLD
        check = np.empty(1,dtype='b')  # variable to get the state of Nest
        while True:
            self.logger.info('Send Nest : loop start : wait all')
            self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
            state_nest = status_.Get_tag()
            for source in source_sending[1:]:
                # improvement: We do not care which source sends first, give MPI the freedom to send in whichever order.
                self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
                if state_nest != status_.Get_tag():
                    raise Exception('Abnormal state : the state of Nest is different between rank')
            self.logger.info("Send Nest : Get check : status : "+str(status_.Get_tag()))

            if status_.Get_tag() == 0:
                # INTERNAL : get the data to send
                # (here is spike trains but Nest can receive other type of data.
                # For the other type of data, the format to send it is different
                self.logger.info("Send Nest : start to send ")
                spikes_times = self.communication_internal.get_spikes()
                self.communication_internal.get_spikes_release()
                self.logger.info("Send Nest : shape buffer "+str(self.communication_internal.shape_buffer[0]))
                if self.communication_internal.shape_buffer[0] == -1:
                    break
                self.logger.info("Send Nest : spike time")

                # Waiting for some processes of Nest to receive the spikes
                for source in source_sending:
                    # improvement: We do not care which source sends first,
                    #   give MPI the freedom to send in whichever order.
                    # receive list ids
                    size_list = np.empty(1, dtype='i')
                    self.port_comms[0].Recv([size_list, 1, MPI.INT], source=source, tag=0, status=status_)
                    if size_list[0] != 0:
                        list_id = np.empty(size_list, dtype='i')
                        self.port_comms[0].Recv([list_id, size_list, MPI.INT], source=status_.Get_source(),
                                            tag=0, status=status_)
                        # Select the good spike train and send it
                        self.logger.info("Send Nest : rank " + str(source) + " list_id " + str(list_id)
                                         + " spikes :" + str(spikes_times[0]))
                        data = []
                        shape = []
                        for i in list_id:
                            shape += [len(spikes_times[i-self.id_first_spike_detector])]
                            data += [spikes_times[i-self.id_first_spike_detector]]
                        send_shape = np.array(np.concatenate(([np.sum(shape)], shape)), dtype='i')
                        # firstly send the size of the spikes train
                        self.port_comms[0].Send([send_shape, MPI.INT], dest=status_.Get_source(), tag=list_id[0])
                        # secondly send the spikes train
                        data = np.concatenate(data).astype('d')
                        self.port_comms[0].Send([data, MPI.DOUBLE], dest=source, tag=list_id[0])
                self.logger.info("Send Nest : end sending")

            elif status_.Get_tag() == 1:
                # ending the run of Nest
                self.logger.info("Send Nest : end run")

            elif status_.Get_tag() == 2:
                self.logger.info("Send Nest : end simulation")
                # INTERNAL : close the buffer
                self.communication_internal.get_spikes_end()
                self.logger.info("Send Nest : send false")
                break

            else:
                raise Exception("bad mpi tag : "+str(status_.Get_tag()))
