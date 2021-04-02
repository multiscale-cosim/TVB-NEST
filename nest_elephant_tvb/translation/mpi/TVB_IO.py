from mpi4py import MPI
from nest_elephant_tvb.translation.mpi.mpi_translator import MPI_communication
import numpy as np

class Send_TVB_Data(MPI_communication):
    def __init__(self,sender_rank,*arg,**karg):
        super().__init__(*arg,**karg)
        self.sender_rank = sender_rank
        self.req_send = None
        self.logger.info("Send TVB Data : end init")

    def get_time_rate(self):
        self.logger.info("Send TVB Data : rate(get) : get time rate")
        if self.req_send is not None:
            self.req_send.wait()
        self.logger.info("Send TVB Data : rate(get) : rate :"+str(self.sender_rank))
        req_time = MPI.COMM_WORLD.irecv(source=self.sender_rank, tag=0)
        times = req_time.wait()
        if times[0] == -1:
            self.logger.info("Send TVB Data : rate(get) : times"+str(self.sender_rank))
            return times, None
        req_data = MPI.COMM_WORLD.irecv(source=self.sender_rank, tag=1)
        self.logger.info("Send TVB Data : rate(get) : data request")
        data = req_data.wait()
        self.logger.info("Send TVB Data : rate(get) : end")
        return times,data

    def release_get_time_rate(self):
        self.logger.info("Send TVB Data : rate(release) : begin")
        self.req_send = MPI.COMM_WORLD.isend(True, dest=self.sender_rank)
        self.logger.info("Send TVB Data : rate(release) : end")

    def end_get_time_rate(self):
        self.logger.info("Send TVB Data : rate(end) : wait time")
        req_time = MPI.COMM_WORLD.irecv(source=self.sender_rank, tag=0)
        times = req_time.wait()
        self.logger.info("Send TVB Data : rate(end) : time "+str(times))
        if times[0] != -1:
            self.logger.info("Send TVB Data : rate(end) : wait data ")
            req_data = MPI.COMM_WORLD.irecv(source=self.sender_rank, tag=1)
            data = req_data.wait()
            self.req_send = MPI.COMM_WORLD.isend(False, dest=self.sender_rank)
        self.logger.info("Send TVB Data : rate(end) : end ")

    # See todo in the beginning, encapsulate I/O, transformer, science parts
    def simulation_time(self):
        '''
        Analysis/Science on INTRAcommunicator (multiple MPI ranks possible).
        TODO: not yet used, see also analysis function below
        Send data to TVB on INTERcommunicator comm_sender (multiple MPI ranks possible).
        Replaces the former 'send' function.
        NOTE: First refactored version -> not pretty, not final.

        TODO: Ugly: 'store' and 'analyse' objects passed through all the way from the beginning.
        TODO: Discuss communication protocol of NEST<->transformer and transformer<->TVB
        '''
        self.logger.info("Send TVB Data : init ")
        count=0
        status_ = MPI.Status()
        while True: # FAT END POINT
            self.logger.info("Send TVB Data : start loop ")
            # TODO: this communication has the 'rank 0' problem described in the beginning
            accept = False
            self.logger.info("Send TVB Data : wait to send " )
            while not accept:
                req = self.port_comm.irecv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG)
                accept = req.wait(status_)
            self.logger.info(" Send TVB Data : send data status : " +str(status_.Get_tag()))
            if status_.Get_tag() == 0:
                self.logger.info("Send TVB Data :  get rate")
                times, data = self.get_time_rate()
                if times[0] == -1:
                    self.logger.info("Send TVB Data : end")
                    break

                # Mark as 'ready to receive next simulation step'
                self.logger.info("Send TVB Data : send ready ")

                ############ OLD Code
                # TODO: this communication has the 'rank 0' problem described in the beginning
                self.logger.info("Send TVB Data : send data :"+str(np.sum(data)) )
                # time of stating and ending step
                self.port_comm.Send([times, MPI.DOUBLE], dest=status_.Get_source(), tag=0)
                # send the size of the rate
                size = np.array(int(data.shape[0]),dtype='i')
                self.port_comm.Send([size,MPI.INT], dest=status_.Get_source(), tag=0)
                # send the rates
                self.port_comm.Send([data,MPI.DOUBLE], dest=status_.Get_source(), tag=0)
                ############ OLD Code end

                self.logger.info("Send TVB Data : end send")
                self.release_get_time_rate()
            elif status_.Get_tag() == 1:
                self.end_get_time_rate()
                self.logger.info("Send TVB Data : end sim")
                break
            else:
                raise Exception("bad mpi tag"+str(status_.Get_tag()))
            count+=1
        self.logger.info('Send TVB Data : End of send function')


class Receive_TVB_Data(MPI_communication):
    def __init__(self,receiver_rank,*arg,**karg):
        super().__init__(*arg,**karg)
        self.receiver_rank = receiver_rank
        self.req_1 = None
        self.req_2 = None
        self.req_check = None
        self.logger.info("Receive TVB Data : end init")

    def send_time_rate(self,time_step,rate):
        self.logger.info("Receive TVB Data : rate(send) : init")
        ready = True
        if self.req_1 is not None:
            self.logger.info("Receive TVB Data : rate(send) : wait request")
            self.req_1.wait()
            self.req_2.wait()
            self.logger.info("Receive TVB Data : rate(send) : wait check")
            ready = self.req_check.wait()
            if not ready:
                return ready
        # time of stating and ending step
        self.req_1 = MPI.COMM_WORLD.isend(time_step, dest=self.receiver_rank, tag=0)
        # send the size of the rate
        self.req_2 = MPI.COMM_WORLD.isend(rate, dest=self.receiver_rank, tag=1)
        self.logger.info("Receive TVB Data : rate(send) : ask check")
        self.req_check = MPI.COMM_WORLD.irecv(source=self.receiver_rank)
        self.logger.info("Receive TVB Data : rate(send) : update buffer")
        return ready

    def end_send_rate_time(self):
        self.logger.info("Receive TVB Data : rate(end) : begin")
        self.req_1 = MPI.COMM_WORLD.isend([-1], dest=self.receiver_rank, tag=0)
        self.logger.info(" Receive TVB Data : rate(end) : end")

    # See todo in the beginning, encapsulate I/O, transformer, science parts
    def simulation_time(self):
        self.logger.info("Receive TVB Data : start")
        # Open the MPI port connection
        status_ = MPI.Status()
        source_sending = np.arange(0,self.port_comm.Get_remote_size(),1)# list of all the process for the commmunication
        while True: # FAT END POINT
            self.logger.info("Receive TVB Data : start loop")
            # Send to all the confirmation of the processus can send data
            requests=[]
            self.logger.info("Receive TVB Data : wait receive ")
            for source in source_sending:
                requests.append(self.port_comm.isend(True,dest=source,tag=0))
            MPI.Request.Waitall(requests)
            self.logger.info("Receive TVB Data : receive all")
            # get the starting and ending time of the simulation to translate
            time_step = np.empty(2, dtype='d')
            self.port_comm.Recv([time_step, 2, MPI.DOUBLE], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
            self.logger.info("Receive TVB Data : get time_step "+str(time_step)+" status : " + str(status_.Get_tag()))
            if status_.Get_tag() == 0:
                #  Get the size of the data
                size = np.empty(1, dtype='i')
                self.port_comm.Recv([size, 1, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
                #  Get the rate
                rate = np.empty(size[0], dtype='d')
                self.port_comm.Recv([rate, size[0], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)
                ready = self.send_time_rate(time_step,rate)
                if not ready:
                    self.logger.info('Receive TVB Data : end : ' + str(ready))
                    break
            elif status_.Get_tag() == 1:
                self.logger.info("Receive TVB Data : end ")
                self.end_send_rate_time()
                self.logger.info("Receive TVB Data : send end ")
                break
            else:
                raise Exception("bad mpi tag"+str(status_.Get_tag()))
