#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import os
import json
import logging

import nest_elephant_tvb.translation.RichEndPoint as REP
import nest_elephant_tvb.translation.mpi_translator as mt


import numpy as np
import os
from mpi4py import MPI
from threading import Thread, Lock
from nest_elephant_tvb.translation.science_tvb_to_nest import generate_data
import logging
import json
import time
import pathlib
import copy


lock_status=Lock() # locker for manage the transfer of data from thread

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


def create_logger(path,name, log_level):
    # Configure logger
    logger = logging.getLogger(name)
    fh = logging.FileHandler(path+'/../../log/'+name+'.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if log_level == 0:
        fh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif  log_level == 1:
        fh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif  log_level == 2:
        fh.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    elif  log_level == 3:
        fh.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    elif  log_level == 4:
        fh.setLevel(logging.CRITICAL)
        logger.setLevel(logging.CRITICAL)

    return logger

if __name__ == "__main__":
    import sys

    if len(sys.argv)!=5:
        print('missing argument')
        exit (1)

    # Parse arguments
    path_config = sys.argv[1]
    id_first_spike_detector = int(sys.argv[2])
    nb_spike_generator = int(sys.argv[3])
    TVB_config = sys.argv[4]

    # object for analysing data
    with open(path_config+'/../../parameter.json') as f:
        parameters = json.load(f)
    param = parameters['param_TR_tvb_to_nest']
    
    
    ############ NEW Code: old logging code copied here for better overview
    log_level = param['level_log']
    logger_master = create_logger(path_config, 'tvb_to_nest_master'+str(id_first_spike_detector), log_level)
    logger_send = create_logger(path_config, 'tvb_to_nest_send'+str(id_first_spike_detector), log_level)
    logger_receive = create_logger(path_config, 'tvb_to_nest_receive'+str(id_first_spike_detector), log_level)
    ############# NEW Code end
    
    
    ############ NEW Code: RICH END POINT for MPI and new connections
    ### contains all MPI connection stuff for proper encapsulation
    ### TODO: make this a proper interface
    # TODO This is still a mess! Here and also in the nest_to_tvb direction
    # TODO Check ALL! the command line arguments of 
    # TODO 'test_translator_nest_to_tvb.py'
    # TODO 'test_translator_tvb_to_nest.py
    # TODO e.g. with '.txt', without. hardcoded path, without, ... etc etc.
    path_to_files_receive = path_config + TVB_config
    # NOTE: only one file with 'path/output/0.txt' instead of number of id_first_spike_detector...correct? see TODO below
    path_to_files_send = os.path.join(path_config, str(id_first_spike_detector) + ".txt")
    comm, comm_receiver, port_receive, comm_sender, port_send = REP.make_connections(path_to_files_receive, path_to_files_send, logger_master)
    # TODO: why is this needed, could not see where this is ever reused.
    # TODO see NOTE above: only path/output/0.txt is reused.
    ''' 
    for i in range(nb_spike_generator):
        # write file with port and unlock
        path_to_files_send = os.path.join(path_config, str(id_first_spike_detector+i) + ".txt")
        fport_send = open(path_to_files_send, "w+")
        fport_send.write(port_send)
        fport_send.close()

        path_to_files_send_unlock = os.path.join(path_config, str(id_first_spike_detector+i) + ".txt.unlock")
        pathlib.Path(path_to_files_send_unlock).touch()
        path_to_files_sends.append(path_to_files_send)
        path_to_files_sends_unlock.append(path_to_files_send_unlock)
    '''
    ############# NEW Code end
    
    
    ############ OLD Code, to be changed to MPI
    generator = generate_data(path_config+'/../../log/',nb_spike_generator,param)

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
    
    '''
    ############ NEW Code: removed threads, used MPI ranks...
    ### TODO: encapsulate loggers
    ### kept all logging stuff here for now to have them in one place
    loggers = [logger_master, logger_receive, logger_send] # list of all the loggers
    mt.init(path, param, comm, comm_receiver, comm_sender, loggers)
    ############ NEW Code end
    '''
    
    
    ############ NEW Code: FAT END POINT for MPI and new connections
    ### contains all MPI connection stuff for proper encapsulation
    ### TODO: make this a proper interface
    REP.close_and_finalize(port_send, port_receive,logger_master)
    ############# NEW Code end
    
    
    logger_master.info('clean file')
    # TODO: ugly solution, all MPI ranks want to delete, only the first one can.
    try:
        os.remove(path_to_files_receive)
        os.remove(path_to_files_send)
    except FileNotFoundError:
        pass 
    logger_master.info('end')
