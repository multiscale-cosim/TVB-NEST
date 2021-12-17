#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import numpy as np
from nest_elephant_tvb.transformation.communication.mpi_io_external import MPICommunicationExtern


class ConsumerNestData(MPICommunicationExtern):
    """
    Class for the receiving data from Nest and transfer them to the transformation function process.
    """

    def simulation_time(self):
        """
        Receive data from Nest and add them in a shared buffer.
        """
        self.logger.info("Consumer Nest : simulation time")
        status_ = MPI.Status()
        num_sending = self.port_comms[0].Get_remote_size()  # The total number of the rank in Nest MPI_COMM_WORLD
        check = np.empty(1, dtype='b')  # variable to get the state of Nest
        shape = np.empty(1, dtype='i')  # variable to receive the shape of the data
        count = 0  # count the number of run
        switch = True
        while True:
            self.logger.info("Consumer Nest : loop start : wait all")
            if switch:
                self.timer.start(1)
            else:
                self.timer.start(2)
            self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
            state_nest = status_.Get_tag()
            for source in range(1, num_sending):
                # improvement: We do not care which source sends first, give MPI the freedom to send in whichever order.
                self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
                if state_nest != status_.Get_tag():
                    raise Exception('Abnormal state : the state of Nest is different between rank')
            if switch:
                self.timer.stop(1)
                switch = False
            else:
                self.timer.stop(2)
                switch = True

            if status_.Get_tag() == 0:
                wait = 0
                self.timer.start(3)
                # INTERNAL :ready to write in the buffer
                self.logger.info("Consumer Nest : prepare buffer")
                self.communication_internal.send_spikes_ready()
                if self.communication_internal.send_spike_exit:
                    self.timer.stop(3)
                    self.logger.info("Consumer Nest : break")
                    break
                self.timer.change(3, 4)

                self.logger.info("Consumer Nest : start get data")
                for source in range(num_sending):
                    # send 'ready' to the nest rank
                    self.port_comms[0].Send([np.array(True, dtype='b'), MPI.BOOL], dest=source, tag=0)
                    if wait == 0:
                        self.timer.change(4, 5)  # wait for receive data + receive data
                    # receive package size info
                    self.port_comms[0].Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                    self.logger.info("Consumer Nest : shape : " + str(self.communication_internal.shape_buffer))
                    # Add data in the buffer
                    self.port_comms[0].Recv([self.communication_internal.databuffer[
                                             self.communication_internal.shape_buffer[0]:], MPI.DOUBLE],
                                            source=source, tag=0, status=status_)
                    self.communication_internal.shape_buffer[0] += shape[0]  # move head
                    # self.logger.info("Consumer Nest : end receive data source "+str(source)+" time :"+str(self.communication_internal.databuffer[self.communication_internal.shape_buffer[0]-1]))
                self.logger.info("Consumer Nest : end receive data")
                self.timer.change(5, 6)  # wait for receive data + receive data

                # INTERNAL : end to write in the buffer
                self.communication_internal.send_spikes()
                self.timer.stop(6)  # wait for receive data + receive data

            elif status_.Get_tag() == 1:
                count += 1
                self.logger.info("Consumer Nest : receive end " + str(count))

            elif status_.Get_tag() == 2:
                self.logger.info("Consumer Nest : end simulation")
                # INTERNAL : close the communication
                self.communication_internal.send_spikes_end()
                self.port_comms[0].Barrier()
                self.logger.info("Consumer Nest : Barrier")
                break

            else:
                raise Exception("Abnormal tag : bad mpi tag" + str(status_.Get_tag()))

        self.logger.info('Consumer Nest : End of receive function')


class ProducerDataNest(MPICommunicationExtern):
    """
    Class for sending data to Nest. The data are from the transformation function.
    """

    def __init__(self, id_first_spike_detector, *arg, **karg):
        """
        Consume dat/spikes trains from Nest
        :param id_first_spike_detector: id of the first spike detector
        :param arg: other parameters
        :param karg: other parameters
        """
        super().__init__(*arg, **karg)
        self.id_first_spike_detector = id_first_spike_detector
        self.logger.info('Produce Nest : end init')

    def simulation_time(self):
        """
        Send data to Nest from a shared buffer
        """
        self.logger.info('Produce Nest : simulation')
        # initialisation variable before the loop
        status_ = MPI.Status()
        source_sending = np.arange(0, self.port_comms[0].Get_remote_size(),
                                   1)  # list of all the rank of Nest MPI_COMM_WORLD
        check = np.empty(1, dtype='b')  # variable to get the state of Nest
        switch = True
        while True:
            self.logger.info('Produce Nest : loop start : wait all')
            if switch:
                self.timer.start(1)
            else:
                self.timer.start(2)
            self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
            state_nest = status_.Get_tag()
            for source in source_sending[1:]:
                # improvement: We do not care which source sends first, give MPI the freedom to send in whichever order.
                self.port_comms[0].Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
                if state_nest != status_.Get_tag():
                    raise Exception('Abnormal state : the state of Nest is different between rank')
            self.logger.info("Produce Nest : Get check : status : " + str(status_.Get_tag()))
            if switch:
                self.timer.stop(1)
                switch = False
            else:
                self.timer.stop(2)
                switch = True

            if status_.Get_tag() == 0:
                self.timer.start(3)
                # INTERNAL : get the data to send
                # (here is spike trains but Nest can receive other type of data.
                # For the other type of data, the format to send it is different
                self.logger.info("Produce Nest : start to send ")
                index = self.communication_internal.get_spikes()
                self.logger.info("Produce Nest : shape buffer " + str(self.communication_internal.shape_buffer[0]))
                if self.communication_internal.shape_buffer[0] == -1:
                    self.timer.stop(3)
                    break
                self.logger.info("Produce Nest : spike time")
                self.timer.change(3, 4)

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
                        self.logger.info("Produce Nest : rank " + str(source) + " list_id " + str(list_id)
                                         + " spikes :" + str(self.communication_internal.databuffer[
                                                             index[0]:index[0 + 1]]))
                        if source == source_sending[0]:
                            self.timer.start(6)
                        data = []
                        shape = []
                        for i in list_id:
                            id_spike_generator = i - self.id_first_spike_detector
                            shape += [index[id_spike_generator + 1] - index[id_spike_generator]]
                            data += [self.communication_internal.databuffer[
                                     index[id_spike_generator]:index[id_spike_generator + 1]]]
                        send_shape = np.array(np.concatenate(([np.sum(shape)], shape)), dtype='i')
                        if source == source_sending[0]:
                            self.timer.stop(6)
                        # firstly send the size of the spikes train
                        self.port_comms[0].Send([send_shape, MPI.INT], dest=status_.Get_source(), tag=list_id[0])
                        # secondly send the spikes train
                        data = np.concatenate(data).astype('d')
                        self.port_comms[0].Send([data, MPI.DOUBLE], dest=source, tag=list_id[0])
                    # self.logger.info('Producer Nest : '+str(size_list))
                self.logger.info("Produce Nest : end sending")
                self.timer.change(4, 5)
                self.communication_internal.get_spikes_release()
                self.timer.stop(5)

            elif status_.Get_tag() == 1:
                # ending the run of Nest
                self.logger.info("Produce Nest : end run")

            elif status_.Get_tag() == 2:
                self.logger.info("Produce Nest : end simulation")
                # INTERNAL : close the buffer
                self.communication_internal.get_spikes_end()
                self.logger.info("Produce Nest : send false")
                self.port_comms[0].Barrier()
                self.logger.info("Produce Nest : Barrier")
                break

            else:
                raise Exception("Abnormal tag : bad mpi tag : " + str(status_.Get_tag()))
