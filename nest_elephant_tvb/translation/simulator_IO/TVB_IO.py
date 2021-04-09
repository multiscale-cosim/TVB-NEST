#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import numpy as np
from nest_elephant_tvb.translation.communication.mpi_io_external import MPI_communication_extern


class Send_TVB_Data(MPI_communication_extern):
    """
    Class for sending data to TVB. The data are from the translated function.
    TVB is only 1 rank.
    """

    def simulation_time(self):
        """
        Send data to TVB from receiving data
        """
        self.logger.info("Send TVB Data : init ")
        status_ = MPI.Status()
        while True:
            self.logger.info("Send TVB Data : start loop : wait TVB")
            # Receive the state of TVB for knowing
            accept = False
            while not accept:
                req = self.port_comms[0].irecv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG)
                accept = req.wait(status_)
            self.logger.info(" Send TVB Data : send data status : "+str(status_.Get_tag()))

            if status_.Get_tag() == 0:
                # INTERNAL : receive the data from translator function
                self.logger.info("Send TVB Data : get rate")
                times, data = self.communication_internal.get_time_rate()
                if self.communication_internal.get_time_rate_exit:
                    self.logger.info("Send TVB Data : end")
                    break

                self.logger.info("Send TVB Data : send data :"+str(np.sum(data)))
                # time of stating and ending step
                self.port_comms[0].Send([times, MPI.DOUBLE], dest=status_.Get_source(), tag=0)
                # send the size of the rate
                size = np.array(int(data.shape[0]), dtype='i')
                self.port_comms[0].Send([size, MPI.INT], dest=status_.Get_source(), tag=0)
                # send the rates
                self.port_comms[0].Send([data, MPI.DOUBLE], dest=status_.Get_source(), tag=0)

                # INTERNAL : end sending data
                self.logger.info("Send TVB Data : end send")
                self.communication_internal.get_time_rate_release()

            elif status_.Get_tag() == 1:
                # INTERNAL : release the communication
                self.communication_internal.get_time_rate_end()
                self.logger.info("Send TVB Data : end sim")
                break

            else:
                raise Exception("Abnormal tag : bad mpi tag"+str(status_.Get_tag()))
        self.logger.info('Send TVB Data : End of send function')


class Receive_TVB_Data(MPI_communication_extern):
    """
    Class for the receiving data from Nest and transfer them to the translation function process.
    TVB is only 1 rank.
    """

    def simulation_time(self):
        """
        Receive data from TVB and transfer them to the translation function.
        """
        self.logger.info("Receive TVB Data : start")
        status_ = MPI.Status()
        while True:
            self.logger.info("Receive TVB Data : start loop : wait all")
            # Send to all the confirmation of the Receiver is ready
            request = [self.port_comms[0].isend(True, dest=0, tag=0)]
            MPI.Request.Waitall(request)
            self.logger.info("Receive TVB Data : receive all")

            # get the starting and ending time of the simulation
            time_step = np.empty(2, dtype='d')
            self.port_comms[0].Recv([time_step, 2, MPI.DOUBLE], source=0, tag=MPI.ANY_TAG, status=status_)
            self.logger.info("Receive TVB Data : get time_step "+str(time_step)+" status : " + str(status_.Get_tag()))

            if status_.Get_tag() == 0:
                # Get the rate
                size = np.empty(1, dtype='i')
                self.port_comms[0].Recv([size, 1, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
                rate = np.empty(size[0], dtype='d')
                self.port_comms[0].Recv([rate, size[0], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)

                # INTERNAL : send rate to the transfer function
                self.communication_internal.send_time_rate(time_step, rate)
                if self.communication_internal.send_time_rate_exit:
                    self.logger.info('Receive TVB Data : end : ' + str(self.communication_internal.send_time_rate_exit))
                    break

            elif status_.Get_tag() == 1:
                self.logger.info("Receive TVB Data : end ")
                # INTERNAL : close communication with translation function
                self.communication_internal.send_time_rate_end()
                self.logger.info("Receive TVB Data : send end ")
                break

            else:
                raise Exception("Abnormal tag: bad mpi tag"+str(status_.Get_tag()))
        self.logger.info('Receive TVB Data : End of send function')
