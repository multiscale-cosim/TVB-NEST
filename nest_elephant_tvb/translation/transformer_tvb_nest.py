# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import time
import numpy as np
from mpi4py import MPI
from nest_elephant_tvb.translation.science_tvb_to_nest import generate_data

from threading import Thread, Lock
import copy

lock_status=Lock() # locker for manage the transfer of data from thread

def init(path_config, nb_spike_generator, id_first_spike_detector, param,
         comm, comm_receiver, comm_sender, loggers):
    '''
    Initialize the transformation with MPI. This is the TVB to NEST direction.
    NOTE: more information will be added with more changes. This is still the very first version!

    TODO: Use RichEndPoints for communication encapsulation
    TODO: Seperate 1)Receive 2)Analysis/Science and 3)Send. See also the many Todos in the code
    TODO: Make use of / enable MPI parallelism! Solve hardcoded communication protocol first
    '''
    
    # destructure logger list to indivual variables
    logger_master, logger_receive, logger_send = loggers
    # science part, see import
    # TODO: use os.path (or similar) for proper file handling.
    # TODO: move this object creation to a proper place. They are passed through many functions.
    generator = generate_data(path_config+'/../../log/',nb_spike_generator,param)
    
    ############ NEW Code: 
    # TODO: future work: mpi parallel, use rank 1-x for science and sending
    # TODO: use this MPI intracommunicator, without receiving rank 0
    # intracomm = comm.Create(comm.Get_group().Excl([0]))
    # create the shared memory block / databuffer
    databuffer = _shared_mem_buffer(comm)
    ############# NEW Code end
    '''
    ############ NEW Code: Receive/analyse/send
    if comm.Get_rank() == 0: # Receiver from NEST, rank 0
        # TODO: The choice of rank 0 here stems from the current communication with NEST. 
        # All MPI communication is done with rank 0 from NESt side.
        # Make this (and the TVB side as well) scalable. 
        _receive(comm_receiver, databuffer, logger_receive)
    else: #  Science/analyse and sender to TVB, rank 1-x
        _send(comm_sender, databuffer, logger_send, store, analyse)
    ############ NEW Code end
    '''
    
    ############ OLD Code, to be changed to MPI
    # variable for communication between thread
    status_data=[0]
    initialisation =np.load(param['init'])
    buffer_spike=[initialisation]
    
    # create the thread for receive and send data
    th_send = Thread(target=send, args=(logger_send,id_first_spike_detector,status_data,buffer_spike, comm_sender))
    th_receive = Thread(target=receive, args=(logger_receive,generator,status_data,buffer_spike, comm_receiver ))

    # start the threads
    # FAT END POINT
    logger_master.info('Start thread')
    th_receive.start()
    th_send.start()
    th_receive.join()
    th_send.join()
    logger_master.info('thread join')
    ############# OLD Code end
    
    ############ NEW Code: disconnect
    # TODO: should this be done here?
    #logger_master.info('Disconnect communicators...')
    #comm_receiver.Disconnect()
    #comm_sender.Disconnect()
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
    


# See todo in the beginning, encapsulate I/O, transformer, science parts
def _send(comm_sender, databuffer, logger, store, analyse):
    pass


def send(logger,id_first_spike_detector,status_data,buffer_spike, comm):
    '''
    the sending part of the translator
    :param logger : logger
    :param nb_spike_generator: the number of spike generator
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer_spike: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    # initialisation variable before the loop
    status_ = MPI.Status()
    source_sending = np.arange(0,comm.Get_remote_size(),1) # list of all the process for the communication
    check = np.empty(1,dtype='b')
    while True: # FAT END POINT
        for source in source_sending:
            comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
        logger.info(" Get check : status : " +str(status_.Get_tag()))
        if status_.Get_tag() == 0:
            logger.info(" TVB to Nest: start to send ")
            # wait until the data are ready to use
            while status_data[0] != 0 and status_data[0] != 2: # FAT END POINT
                time.sleep(0.001)
                pass
            spikes_times = copy.deepcopy(buffer_spike[0])
            logger.info(" TVB to Nest: spike time")
            with lock_status:
                if status_data[0] != 2:
                    status_data[0] = 1
            # Waiting for some processus ask for receive the spikes
            for source in source_sending:
                # receive list ids
                size_list = np.empty(1, dtype='i')
                comm.Recv([size_list, 1, MPI.INT], source=source, tag=0, status=status_)
                if size_list[0] != 0:
                    list_id = np.empty(size_list, dtype='i')
                    comm.Recv([list_id, size_list, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
                    # Select the good spike train and send it
                    # logger.info(" TVB to Nest:"+str(data))
                    logger.info("rank "+str(source)+" list_id "+str(list_id))
                    data = []
                    shape = []
                    for i in list_id:
                        shape += [spikes_times[i-id_first_spike_detector].shape[0]]
                        data += [spikes_times[i-id_first_spike_detector]]
                    send_shape = np.array(np.concatenate(([np.sum(shape)],shape)), dtype='i')
                    # firstly send the size of the spikes train
                    comm.Send([send_shape, MPI.INT], dest=status_.Get_source(), tag=list_id[0])
                    # secondly send the spikes train
                    data = np.concatenate(data).astype('d')
                    comm.Send([data, MPI.DOUBLE], dest=source, tag=list_id[0])
            logger.info(" end sending:")
        elif  status_.Get_tag() == 1:
            # ending the update of the all the spike train from one processus
            logger.info(" TVB to Nest end sending ")
        elif status_.Get_tag() == 2:
            logger.info(" TVB to Nest end simulation ")
            with lock_status:
                status_data[0] = 2
            break
        else:
            raise Exception("bad mpi tag : "+str(status_.Get_tag()))
    logger.info('communication disconnect')
    comm.Disconnect()
    logger.info('end thread')
    return


def receive(logger,generator,status_data,buffer_spike, comm):
    '''
    the receiving part of the translator
    :param logger : logger
    :param generator : the function to generate rate to spikes
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer_spike: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    # Open the MPI port connection
    status_ = MPI.Status()
    source_sending = np.arange(0,comm.Get_remote_size(),1)# list of all the process for the commmunication
    while True: # FAT END POINT
        # Send to all the confirmation of the processus can send data
        requests=[]
        logger.info(" TVB to Nest: wait receive ")
        for source in source_sending:
            requests.append(comm.isend(True,dest=source,tag=0))
        MPI.Request.Waitall(requests)
        logger.info(" TVB to Nest: receive all")
        # get the starting and ending time of the simulation to translate
        time_step = np.empty(2, dtype='d')
        comm.Recv([time_step, 2, MPI.DOUBLE], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        logger.info(" TVB to Nest: get time_step "+str(time_step)+" status : " + str(status_.Get_tag()))
        if status_.Get_tag() == 0:
            #  Get the size of the data
            size = np.empty(1, dtype='i')
            comm.Recv([size, 1, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
            #  Get the rate
            rate = np.empty(size[0], dtype='d')
            comm.Recv([rate, size[0], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)
            spike_generate = generator.generate_spike(0,time_step,rate)
            logger.info(" TVB to Nest: wait status")
            # Wait for lock to be set to False
            while status_data[0] != 1 and status_data[0] != 2:
                time.sleep(0.001)
                pass
            # Set lock to true and put the data in the shared buffer
            buffer_spike[0] = spike_generate
            logger.info(" TVB to Nest: update buffer")
            with lock_status:
                status_data[0] = 0
        elif status_.Get_tag() == 1:
            with lock_status:
                status_data[0] = 2
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))
    logger.info('communication disconnect')
    comm.Disconnect()
    logger.info('end thread')
    return
