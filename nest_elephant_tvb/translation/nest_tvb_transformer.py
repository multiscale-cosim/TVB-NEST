# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import time
import numpy as np
from mpi4py import MPI
from nest_elephant_tvb.translation.science_nest_to_tvb import store_data,analyse_data

def init(path, param, comm, comm_receiver, comm_sender, loggers):
    '''
    Initialize the translation with MPI.
    NOTE: more information will be added with more changes. This is still the very first version!
    
    TODO: IMPORTANT!!! MPI communication on NEST and TVB side is somewhat hardcoded.
        --> NEST sends to and receives from rank 0 on transformer side. This works here, since rank 0 is the receiving rank
            --> https://github.com/sdiazpier/nest-simulator/blob/nest-i/nestkernel/recording_backend_mpi.cpp
            --> line 396 ff (as of Feb 17th, 2021)
        --> TVB sends and receives from rank 0 on transformer side.
            --> nest_elephant_tvb/translation/test_file/test_receive_nest_to_tvb.py
            --> line 32 ff (as of Feb 17th, 2021)
            --> Here: Rank 1-x are doing analysis/science and sending to TVB
            --> For now, hardcoded solution. All places with 'rank 0' are replaced with 'rank 1'
            --> But as soon as we use more than two MPI ranks, this fails again!!!
    
    TODO: Renaming! Translator -> transformer, etc.
    TODO: This is only the Nest to TVB direction. For other direction some generalizing changes will be needed.
    TODO: Use RichEndPoints for communication encapsulation
    TODO: Seperate 1)Receive 2)Analysis/Science and 3)Send. See also the many Todos in the code
    TODO: Make use of / enable MPI parallelism! Solve hardcoded communication protocol first
    '''
    
    # destructure logger list to indivual variables
    logger_master, logger_receive, logger_send = loggers
    # science part, see import
    # TODO: use os.path (or similar) for proper file handling.
    # TODO: move this object creation to a proper place. They are passed through many functions.
    store = store_data(path+'/log/',param)
    analyse = analyse_data(path+'/log/',param)
    
    ############ NEW Code: 
    # TODO: future work: mpi parallel, use rank 1-x for science and sending
    # TODO: use this MPI intracommunicator, without receiving rank 0
    # intracomm = comm.Create(comm.Get_group().Excl([0]))
    # create the shared memory block / databuffer
    databuffer = _shared_mem_buffer(comm)
    ############# NEW Code end
    
    ############ NEW Code: Receive/analyse/send
    if comm.Get_rank() == 0: # Receiver from NEST, rank 0
        # TODO: The choice of rank 0 here stems from the current communication with NEST. 
        # All MPI communication is done with rank 0 from NESt side.
        # Make this (and the TVB side as well) scalable. 
        _receive(comm_receiver, databuffer, logger_receive)
    else: #  Science/analyse and sender to TVB, rank 1-x
        _send(comm_sender, databuffer, logger_send, store, analyse)
    ############ NEW Code end
    
    ############ NEW Code: disconnect
    # TODO: should this be done here?
    logger_master.info('Disconnect communicators...')
    comm_receiver.Disconnect()
    comm_sender.Disconnect()
    ############ NEW Code end


def _shared_mem_buffer(comm):
    '''
    Create shared memory buffer. MPI One-sided-Communication.
    :param comm: MPI intra communicator to create the buffer.
    :return buffer: 1D shared memory buffer array 
    
    TODO: Buffersize/max. expected number of events hardcoded
    -> free param, handle properly!
    Explanation:
    -> each package from NEST contains a continuous list of the events of the current simulation step
    -> the number of events in each package is unknown and not constant
    -> each event is three doubles: Id_recording_device, neuronID, spiketimes
    
    TODO: reshaping of the buffer content is done in the science part
    -> 1D array to shape (x,3) where x is the number of events.
    -> this is decided by the nest I/O part, i.e. nest sends out events in 1D array 
    -> can/should this be more generic?
    '''
    datasize = MPI.DOUBLE.Get_size()
    bufsize = 1000000 * 3 # NOTE: hardcoded (max.expected events per package from nest)
    if comm.Get_rank() == 0:
        bufbytes = datasize * bufsize
    else: 
        bufbytes= 0
    # rank 0: create the shared block
    # rank 1-x: get a handle to it
    win = MPI.Win.Allocate_shared(bufbytes, datasize, comm=comm)
    buf, datasize = win.Shared_query(0)
    assert datasize == MPI.DOUBLE.Get_size()
    # create a numpy array (buffer) whose data points to the shared mem
    return np.ndarray(buffer=buf, dtype='d', shape=(bufsize,))


# See todo in the beginning, encapsulate I/O, transformer, science parts
def _receive(comm_receiver, databuffer, logger):
    '''
    Receive data on rank 0. Put it into the shared mem buffer.
    Replaces the former 'receive' function.
    NOTE: First refactored version -> not pretty, not final. 
    '''
    status_ = MPI.Status()
    num_sending = comm_receiver.Get_remote_size() # how many NEST ranks are sending?
    # TODO: It seems the 'check' variable is used to receive tags from NEST, i.e. ready for send...
    # change this in the future, also mentioned in the FatEndPoint solution from Wouter.
    check = np.empty(1,dtype='b')
    shape = np.empty(1, dtype='i')    
    count = 0
    # TODO: the last two buffer entries are used for shared information
    # --> they replace the status_data variable from previous version
    # --> find more elegant solution?
    databuffer[-1] = 1 # set buffer to 'ready to receive from nest'
    databuffer[-2] = 0 # marks the 'head' of the buffer
    
    while(True):
        logger.info(" Nest to TVB : wait all")
        head_ = 0 # head of the buffer, reset after each iteration
         
        # TODO: This is still not correct. We only check for the Tag of the last rank.
        # TODO: IF all ranks send always the same tag in one iteration (simulation step)
        # TODO: then this works. But it should be handled differently!!!!
        for i in range(num_sending):
            # new: We do not care which source sends first, give MPI the freedom to send in whichever order.
            comm_receiver.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        # TODO: handle properly, all ranks send tag 0?
        if status_.Get_tag() == 0:
            # wait until ready to receive new data (i.e. the sender has cleared the buffer)
            while databuffer[-1] != 1: # TODO: use MPI, remove the sleep
                time.sleep(0.001)
                pass
            for source in range(num_sending):
                # send 'ready' to the nest rank
                comm_receiver.Send([np.array(True,dtype='b'),MPI.BOOL],dest=source,tag=0)
                # receive package size info
                comm_receiver.Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                # NEW: receive directly into the buffer
                comm_receiver.Recv([databuffer[head_:], MPI.DOUBLE], source=source, tag=0, status=status_)
                head_ += shape[0] # move head 
                # TODO: revisit and check for proper encapsulation
                # Here, storing and adding the spikes to the histogram was done
                # Old code: store.add_spikes(count,data)
                # This increased the workload of this MPI rank.
                # All science and analysis stuff is moved to the 'sender' part. Because future parallel.
            # Mark as 'ready to do analysis'
            databuffer[-1] = 0
            # important: head_ is first buffer index WITHOUT data.
            databuffer[-2] = head_
        # TODO: handle properly, all ranks send tag 1?
        elif status_.Get_tag() == 1:
            count += 1
            logger.info("Nest to TVB : receive end " + str(count))
        # TODO: handle properly, all ranks send tag 2?
        elif status_.Get_tag() == 2:
            logger.info("end simulation")
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))
    
    logger.info('NEST_to_TVB: End of receive function')


# See todo in the beginning, encapsulate I/O, transformer, science parts
def _send(comm_sender, databuffer, logger, store, analyse):
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
    while True: # FAT END POINT
        # TODO: this communication has the 'rank 0' problem described in the beginning
        accept = False
        logger.info("Nest to TVB : wait to send " )
        while not accept:
            req = comm_sender.irecv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG)
            accept = req.wait(status_)
        logger.info(" Nest to TVB : send data status : " +str(status_.Get_tag()))
        if status_.Get_tag() == 0:
            # wait until the receiver has cleared the buffer, i.e. filled with new data
            while databuffer[-1] != 0: # TODO: use MPI, remove the sleep
                time.sleep(0.001)
                pass
            # TODO: All science/analysis here. Move to a proper place.
            times,data = _analyse(count, databuffer, store, analyse)
            
            # Mark as 'ready to receive next simulation step'
            databuffer[-1] = 1
            
            ############ OLD Code
            # TODO: this communication has the 'rank 0' problem described in the beginning
            logger.info("Nest to TVB : send data :"+str(np.sum(data)) )
            # time of stating and ending step
            comm_sender.Send([times, MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            # send the size of the rate
            size = np.array(int(data.shape[0]),dtype='i')
            comm_sender.Send([size,MPI.INT], dest=status_.Get_source(), tag=0)
            # send the rates
            comm_sender.Send([data,MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            ############ OLD Code end
        elif status_.Get_tag() == 1:
            # disconnect when everything is ending
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))
        count+=1
    logger.info('NEST_to_TVB: End of send function')


# See todo in the beginning, encapsulate I/O, transformer, science parts
def _analyse(count, databuffer, store, analyse):
    '''
    All analysis and science stuff in one place.
    Done in three steps, that were previously disconnected.
    Step 1 and 2 were done in the receiving thread, step 3 in the sending thread.
    NOTE: All science and analysis is the same as before.
    :param count: Simulation iteration/step
    :param databuffer: The buffer contains the spikes of the current step
    :param store: Python object, create the histogram 
    :param analyse: Python object, calculate rates
    :return times, data: simulation times and the calculated rates
    
    TODO: Step 1 and 2 can be merged into one step. Buffer is no longer filled rank by rank.
    TODO: Make this parallel with the INTRA communicator (should be embarrassingly parallel).
    '''
    # Step 1) take all data from buffer and create histogram
    # second to last index in databuffer denotes how much data there is
    store.add_spikes(count,databuffer[:int(databuffer[-2])])
    # Step 2) take the resulting histogram
    data_to_analyse = store.return_data()
    # Step 3) Analyse this data, i.e. calculate rates?
    times,data = analyse.analyse(count,data_to_analyse)
    
    return times, data
