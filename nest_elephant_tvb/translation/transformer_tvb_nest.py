# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import time
import numpy as np
from mpi4py import MPI
from nest_elephant_tvb.translation.science_tvb_to_nest import generate_data

def init(path_config, nb_spike_generator, id_first_spike_detector, param,
         comm, comm_receiver, comm_sender, loggers):
    '''
    Initialize the transformation with MPI. This is the TVB to NEST direction.
    NOTE: more information will be added with more changes. This is still the very first version!

    TODO: Use RichEndPoints for communication encapsulation
    TODO: Seperate 1)Receive 2)Analysis/Science and 3)Send. See also the many Todos in the code
    TODO: Make use of / enable MPI parallelism! Solve hardcoded communication protocol first
    
    TODO: This side mirrors the NEST to TVB side
    -> TVB communicates on rank 0
    -> NEST communcates on rank 1
    This is vice versa in the nest to tvb direction.
    TODO: solve this together with the rest of the communication protocol.
    '''
   
    # destructure logger list to indivual variables
    logger_master, logger_receive, logger_send = loggers
    # science part, see import
    # TODO: use os.path (or similar) for proper file handling.
    # TODO: move this object creation to a proper place. They are passed through many functions.
    generator = generate_data(path_config+'/log/',nb_spike_generator,param)
 
    ############ NEW Code: 
    # TODO: future work: mpi parallel, use rank 1-x for science and sending
    # TODO: use this MPI intracommunicator, without receiving rank 0
    # intracomm = comm.Create(comm.Get_group().Excl([0]))
    # create the shared memory block / databuffer
    databuffer = _shared_mem_buffer(comm)
    ############# NEW Code end
   
    ############ NEW Code: Receive/analyse/send
    if comm.Get_rank() == 0: # Receiver from TVB
        # All MPI communication is done with rank 0 from TVB side
        # Make this (and the NEST side as well) scalable. 
        _receive(comm_receiver, databuffer, logger_receive)
    else: #  Science/generate and sender to NEST, rank 1-x
        _send(comm_sender, databuffer, logger_send, generator, id_first_spike_detector)
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
    
    TODO: Buffersize/max. expected size of incoming data
    -> free param, handle properly!
    TODO: 2 doubles: [start_time,end_time] of simulation step
    TODO: unknown number of doubles: array with rates
    '''
    datasize = MPI.DOUBLE.Get_size()
    bufsize = 2 + 1000000 # NOTE: hardcoded (max.expected size of rate array)
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
    num_sending = comm_receiver.Get_remote_size() # how many TVB ranks are sending?
    # init placeholder for incoming data
    time_step = np.empty(2, dtype='d') # two doubles with start and end time of the step
    size = np.empty(1, dtype='i') # size of the rate-array
    # TODO: the last two buffer entries are used for shared information
    # --> they replace the status_data variable from previous version
    # --> find more elegant solution?
    databuffer[-1] = 1 # set buffer to 'ready to receive from tvb'
    databuffer[-2] = 0 # marks the 'head' of the buffer
    
    while True:
        # TODO: NEST to TVB transformer: irecv
        # TODO: TVB to NEST transformer (here): isend
        # TODO: --> rework communication protocol between simulators and transformers!
        requests=[]
        logger.info(" TVB to Nest: wait receive ")
        for rank in range(num_sending):
            requests.append(comm_receiver.isend(True,dest=rank,tag=0))
        MPI.Request.Waitall(requests)
        logger.info(" TVB to Nest: receive all")
        
        # TODO: works for now, needs rework if multiple ranks are used on TVB side
        # TODO: we receive from "ANY_SOURCE", but only check the status_ of the last receive...
        # get the starting and ending time of the simulation step
        # NEW: receive directly into the buffer
        comm_receiver.Recv([databuffer[0:], MPI.DOUBLE], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        logger.info(" TVB to Nest: get time_step "+str(time_step)+" status : " + str(status_.Get_tag()))
        if status_.Get_tag() == 0:
            # wait until ready to receive new data (i.e. the sender has cleared the buffer)
            while databuffer[-1] != 1: # TODO: use MPI, remove the sleep
                time.sleep(0.001)
                pass
            # Get the size of the data
            comm_receiver.Recv([size, 1, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
            # NEW: receive directly into the buffer
            # First two entries are the times, see above
            comm_receiver.Recv([databuffer[2:], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)
            # Mark as 'ready to do analysis'
            databuffer[-1] = 0
            databuffer[-2] = size # info about size of data array
            logger.info(" TVB to Nest: update buffer")
        elif status_.Get_tag() == 1:
            logger.info('TVB: end simulation')
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))
    
    logger.info('TVB_to_NEST: End of receive function')


# See todo in the beginning, encapsulate I/O, transformer, science parts
def _send(comm_sender, databuffer, logger, generator, id_first_spike_detector):
    '''
    Generator/Science on INTRAcommunicator (multiple MPI ranks possible).
    TODO: not yet used.
    Send data to NEST on INTERcommunicator comm_sender (multiple MPI ranks possible).
    Replaces the former 'send' function.
    NOTE: First refactored version -> not pretty, not final. 
    
    TODO: Discuss communication protocol of TVB<->transformer and transformer<->NEST
    '''
    status_ = MPI.Status()
    num_sending = comm_sender.Get_remote_size() # how many TVB ranks are sending?
    # init placeholder for incoming data
    check = np.empty(1,dtype='b')
    size_list = np.empty(1, dtype='i')
    logger.info('starting sending loop')
    while(True):
        # TODO: This is still not correct. We only check for the Tag of the last rank.
        # TODO: IF all ranks send always the same tag in one iteration (simulation step)
        # TODO: then this works. But it should be handled differently!!!!
        for rank in range(num_sending):
            comm_sender.Recv([check, 1, MPI.CXX_BOOL], source=rank, tag=MPI.ANY_TAG, status=status_)
        logger.info("TVB to NEST : send data status : " +str(status_.Get_tag()))
        # TODO: handle properly, all ranks send tag 0?
        if status_.Get_tag() == 0:
            # wait until the receiver has cleared the buffer, i.e. filled with new data
            while databuffer[-1] != 0: # TODO: use MPI, remove the sleep
                time.sleep(0.001)
                pass

            # TODO: All science/generate here. Move to a proper place.
            # method: generate_spike(count,time_step,rate)
            # NOTE: count is a hardcoded '0'. Why?
            # NOTE: time_step are the first two doubles in the buffer
            # NOTE: rate is a double array, which size is stored in the second to last index
            spikes_times = generator.generate_spike(0,databuffer[:2],databuffer[2:int(databuffer[-2])])
            logger.info(" TVB to Nest: spike time")
            
            # Mark as 'ready to receive next simulation step'
            databuffer[-1] = 1
            
            ###### OLD code, kept the communication and science as it is for now
            ### TODO: Receive from status_.Get_source() and rank
            ### TODO: Send to status_.Get_source() and rank
            ### TODO: why???
            ### TODO: a second status_ object is used, should not be named the same
            for rank in range(num_sending):
                # NOTE: in 'test_receive_tvb_to_nest.py': hardcoded 10
                comm_sender.Recv([size_list, 1, MPI.INT], source=rank, tag=0, status=status_)
                if size_list[0] != 0:
                    list_id = np.empty(size_list, dtype='i')
                    # NOTE: in 'test_receive_tvb_to_nest.py': hardcoded np.arange(0,10,1)
                    comm_sender.Recv([list_id, size_list, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
                    # Select the good spike train and send it
                    # logger.info(" TVB to Nest:"+str(data))
                    logger.info("rank "+str(rank)+" list_id "+str(list_id))
                    # TODO: Creating empty lists and append to them in a loop, all inside a loop
                    # TODO: this is slow and will be a bottleneck when we scale up.
                    data = []
                    shape = []
                    for i in list_id:
                        shape += [spikes_times[i-id_first_spike_detector].shape[0]]
                        data += [spikes_times[i-id_first_spike_detector]]
                    send_shape = np.array(np.concatenate(([np.sum(shape)],shape)), dtype='i')
                    # firstly send the size of the spikes train
                    comm_sender.Send([send_shape, MPI.INT], dest=status_.Get_source(), tag=list_id[0])
                    # secondly send the spikes train
                    data = np.concatenate(data).astype('d')
                    comm_sender.Send([data, MPI.DOUBLE], dest=rank, tag=list_id[0])
            logger.info(" end sending:")
            ###### OLD code end
        elif  status_.Get_tag() == 1:
            logger.info(" TVB to Nest end sending") # NOTE: one sim step?
        elif status_.Get_tag() == 2:
            logger.info(" TVB to Nest end simulation ") # NOTE: end whole sim.
            break
        else:
            raise Exception("bad mpi tag : "+str(status_.Get_tag()))
    
    logger.info('TVB_to_NEST: End of send function')
