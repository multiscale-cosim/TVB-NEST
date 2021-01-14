import time
import numpy as np
from mpi4py import MPI
from threading import Thread, Lock
from nest_elephant_tvb.translation.science_nest_to_tvb import store_data,analyse_data

lock_status=Lock() # locker for manage the transfer of data from thread

def init(path, param, comm, comm_receiver, comm_sender, loggers):
    '''
    Initialize the translation with MPI
    
    '''
    
    # destructure logger list to indivual variables
    logger_master, logger_receive, logger_send = loggers
    # science part, see import
    store = store_data(path+'/log/',param)
    analyse = analyse_data(path+'/log/',param)
    # variable for communication between thread
    status_data=[0] # status of the buffer
    
    ############ NEW Code: MPI intracommunicator
    # receive on rank 0, science and send on rank 1
    # TODO: future work: mpi parallel, use rank 1-x for science and sending
    # NOTE: still copy-paste from kim master thesis code....
    # new server-intracommunicator without receiving rank 0
    intracomm = comm.Create(comm.Get_group().Excl([0]))
    # create the shared memory block / databuffer
    buf_pkgs = 100 # NOTE: size hardcoded!
    databuffer = _shared_mem_buffer(buf_pkgs,100,comm)
    ############# NEW Code end
    
    # TODO:
    # 1) receive package from nest, store in shared mem buffer
    # 2) take from shared mem buffer, do science, send to tvb
    # solve issues:
    # - one package incoming, one package outgoing (synchronize)
    # - mark buffer if new package arrived --> not to slow not to fast 
    # - FIRST idea: 
    #   - Receiving rank 0 check for 'NaN' in buffer, i.e. is it empty?
    #   - if NaN then fill with new package
    #   - Sending rank 1 (or more in the future) check for new package in buffer (not NaN)
    #   - do science and send to TVB
    #   - set buffer to NaN to mark as ready
    # TODO: how to check for END of simulation?
    
    ############ OLD Code to replace: with threads, current solution
    initialisation =np.load(param['init']) # initialisation value
    buffer=[initialisation] # buffer of the rate to send it
        
    # create the thread for receive and send data
    th_receive = Thread(target=receive, args=(logger_receive,store,status_data,buffer, comm_receiver))
    th_send = Thread(target=send, args=(logger_send,analyse,status_data,buffer, comm_sender))

    # start the threads
    # FAT END POINT
    logger_master.info('Start thread')
    th_receive.start()
    th_send.start()
    th_receive.join()
    th_send.join()
    logger_master.info('thread join')
    ############# OLD Code end


def _shared_mem_buffer(buf_pkgs,sizes,comm):
    '''
    Create a shared memory block.
    MPI One-sided-Communication.
    NOTE: still copy-paste from kim master thesis code...
    '''
    pkg_size = np.sum(sizes)
    datasize = MPI.DOUBLE.Get_size()
    if comm.Get_rank() == 0:
        bufbytes = buf_pkgs * datasize*2 * pkg_size 
    else: 
        bufbytes= 0
    # rank 0: create the shared block
    # rank 1-x: get a handle to it
    win = MPI.Win.Allocate_shared(bufbytes, datasize, comm=comm)
    buf, datasize = win.Shared_query(0) 
    assert datasize == MPI.DOUBLE.Get_size()
    # create a numpy array (buffer) whose data points to the shared mem
    return np.ndarray(buffer=buf, dtype='d', shape=(buf_pkgs*pkg_size,2))



def receive(logger,store,status_data,buffer, comm):
    '''
    the receive part of the translator
    :param logger : logger fro the thread
    :param store : object for store the data before analysis
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    # initialise variables for the loop
    status_ = MPI.Status() # status of the different message
    source_sending = np.arange(0,comm.Get_remote_size(),1) # list of all the process for the commmunication
    check = np.empty(1,dtype='b')
    count=0
    while True: # FAT END POINT
        # send the confirmation of the process can send data
        logger.info(" Nest to TVB : wait all")
        for source in source_sending:
            comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)

        if status_.Get_tag() == 0:
            logger.info(" Nest to TVB : start to receive")
            #  Get the data/ spike
            for source in source_sending:
                comm.Send([np.array(True,dtype='b'),MPI.BOOL],dest=source,tag=0)
                shape = np.empty(1, dtype='i')
                comm.Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                data = np.empty(shape[0], dtype='d')
                comm.Recv([data, shape[0], MPI.DOUBLE], source=source, tag=0, status=status_)
                store.add_spikes(count,data)
            while status_data[0] != 1 and status_data[0] != 2: # FAT END POINT
                time.sleep(0.001)
                pass
            # wait until the data can be send to the sender thread
            # Set lock to true and put the data in the shared buffer
            buffer[0] = store.return_data()
            with lock_status: # FAT END POINT
                if status_data[0] != 2:
                    status_data[0] = 0
        elif status_.Get_tag() == 1:
            logger.info("Nest to TVB : receive end " + str(count))
            count += 1
        elif status_.Get_tag() == 2:
            with lock_status:
                status_data[0] = 2
            logger.info("end simulation")
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))
    logger.info('communication disconnect')
    comm.Disconnect()
    logger.info('end thread')
    return


def send(logger,analyse,status_data,buffer, comm):
    '''
    the sending part of the translator
    :param logger: logger fro the thread
    :param analyse ; analyse object to transform spikes to state variable
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    count=0
    status_ = MPI.Status()
    while True: # FAT END POINT
        # wait until the translator accept the connections
        accept = False
        logger.info("Nest to TVB : wait to send " )
        while not accept:
            req = comm.irecv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG)
            accept = req.wait(status_)
        logger.info(" Nest to TVB : send data status : " +str(status_.Get_tag()))
        if status_.Get_tag() == 0:
            # send the rate when there ready
            while status_data[0] != 0: # FAT END POINT
                time.sleep(0.001)
                pass
            times,data=analyse.analyse(count,buffer[0])
            with lock_status:
                if status_data[0] != 2:
                    status_data[0] = 1
            logger.info("Nest to TVB : send data :"+str(np.sum(data)) )
            # time of stating and ending step
            comm.Send([times, MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            # send the size of the rate
            size = np.array(int(data.shape[0]),dtype='i')
            comm.Send([size,MPI.INT], dest=status_.Get_source(), tag=0)
            # send the rates
            comm.Send([data,MPI.DOUBLE], dest=status_.Get_source(), tag=0)
        elif status_.Get_tag() == 1:
            # disconnect when everything is ending
            with lock_status:
                status_data[0] = 2
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))
        count+=1
    logger.info('communication disconnect')
    comm.Disconnect()
    logger.info('end thread')
    return
