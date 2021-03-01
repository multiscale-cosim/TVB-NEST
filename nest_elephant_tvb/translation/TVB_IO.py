from mpi4py import MPI
from nest_elephant_tvb.translation.mpi_translator import MPI_communication
import numpy as np

class Send_TVB_Data(MPI_communication):
    def __init__(self,sender_rank,*arg,**karg):
        super().__init__(*arg,**karg)
        self.sender_rank = sender_rank

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

        count=0
        status_ = MPI.Status()
        req_send = None
        while True: # FAT END POINT
            # TODO: this communication has the 'rank 0' problem described in the beginning
            accept = False
            self.logger.info("Nest to TVB : wait to send " )
            while not accept:
                req = self.port_comm.irecv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG)
                accept = req.wait(status_)
            self.logger.info(" Nest to TVB : send data status : " +str(status_.Get_tag()))
            if status_.Get_tag() == 0:

                # TODO: All science/analysis here. Move to a proper place.
                if req_send is not None:
                    req_send.wait()
                req_time = MPI.COMM_WORLD.irecv(source=self.sender_rank,tag=0)
                times = req_time.wait()
                if times[0] == -1:
                    break
                req_data = MPI.COMM_WORLD.irecv(source=self.sender_rank,tag=1)
                data = req_data.wait()

                # Mark as 'ready to receive next simulation step'
                self.logger.info("Nest to TVB : send ready ")

                ############ OLD Code
                # TODO: this communication has the 'rank 0' problem described in the beginning
                self.logger.info("Nest to TVB : send data :"+str(np.sum(data)) )
                # time of stating and ending step
                self.port_comm.Send([times, MPI.DOUBLE], dest=status_.Get_source(), tag=0)
                # send the size of the rate
                size = np.array(int(data.shape[0]),dtype='i')
                self.port_comm.Send([size,MPI.INT], dest=status_.Get_source(), tag=0)
                # send the rates
                self.port_comm.Send([data,MPI.DOUBLE], dest=status_.Get_source(), tag=0)
                ############ OLD Code end
                req_send = MPI.COMM_WORLD.isend(True, dest=self.sender_rank)
            elif status_.Get_tag() == 1:
                req_time = MPI.COMM_WORLD.irecv(source=self.sender_rank,tag=0)
                times = req_time.wait()
                if times[0] != -1:
                    req_data = MPI.COMM_WORLD.irecv(source=self.sender_rank,tag=1)
                    data = req_data.wait()
                    req_send = MPI.COMM_WORLD.isend(False, dest=self.sender_rank)
                break
            else:
                raise Exception("bad mpi tag"+str(status_.Get_tag()))
            count+=1
        self.logger.info('NEST_to_TVB: End of send function')


class Receive_TVB_Data(MPI_communication):
    def __init__(self,receiver_rank,*arg,**karg):
        super().__init__(*arg,**karg)
        self.receiver_rank = receiver_rank


    # See todo in the beginning, encapsulate I/O, transformer, science parts
    def simulation_time(self):
        # Open the MPI port connection
        status_ = MPI.Status()
        source_sending = np.arange(0,self.port_comm.Get_remote_size(),1)# list of all the process for the commmunication
        req_1 = None
        req_2 = None
        req_check = None
        while True: # FAT END POINT
            # Send to all the confirmation of the processus can send data
            requests=[]
            self.logger.info(" TVB to Nest: wait receive ")
            for source in source_sending:
                requests.append(self.port_comm.isend(True,dest=source,tag=0))
            MPI.Request.Waitall(requests)
            self.logger.info(" TVB to Nest: receive all")
            # get the starting and ending time of the simulation to translate
            time_step = np.empty(2, dtype='d')
            self.port_comm.Recv([time_step, 2, MPI.DOUBLE], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
            self.logger.info(" TVB to Nest: get time_step "+str(time_step)+" status : " + str(status_.Get_tag()))
            if status_.Get_tag() == 0:
                #  Get the size of the data
                size = np.empty(1, dtype='i')
                self.port_comm.Recv([size, 1, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
                #  Get the rate
                rate = np.empty(size[0], dtype='d')
                self.port_comm.Recv([rate, size[0], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)
                if req_1 is not None:
                    req_1.wait()
                    req_2.wait()
                    ready = req_check.wait()
                    if not ready:
                        self.logger.info('end : ' + str(ready))
                        break
                # time of stating and ending step
                req_1 = MPI.COMM_WORLD.isend(time_step, dest=self.receiver_rank, tag=0)
                # send the size of the rate
                req_2 = MPI.COMM_WORLD.isend(rate, dest=self.receiver_rank, tag=1)
                req_check = MPI.COMM_WORLD.irecv(source=self.receiver_rank)
                self.logger.info(" TVB to Nest: update buffer")
            elif status_.Get_tag() == 1:
                self.logger.info(" TVB to Nest: end ")
                req_1 = MPI.COMM_WORLD.isend([-1], dest=self.receiver_rank, tag=0)
                self.logger.info(" send end ")
                break
            else:
                raise Exception("bad mpi tag"+str(status_.Get_tag()))
