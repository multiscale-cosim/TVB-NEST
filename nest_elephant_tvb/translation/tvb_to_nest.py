#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
import os
from mpi4py import MPI
from threading import Thread, Lock
from nest_elephant_tvb.translation.science_tvb_to_nest import generate_data
import logging
import json
import time
import pathlib
from timer.Timer import Timer

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
    timer_send = Timer(5,100000)
    timer_send.start(0)
    # initialisation variable before the loop
    status_ = MPI.Status()
    source_sending = np.arange(0,comm.Get_remote_size(),1) # list of all the process for the communication
    check = np.empty(1,dtype='b')
    timer_send.stop(0)
    while True: # FAT END POINT
        timer_send.start(1)
        for source in source_sending:
            comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
        logger.info(" Get check : status : " +str(status_.Get_tag()))
        timer_send.stop(1)
        if status_.Get_tag() == 0:
            logger.info(" TVB to Nest: start to send ")
            # wait until the data are ready to use
            timer_send.start(2)
            while status_data[0] != 0 and status_data[0] != 2: # FAT END POINT
                time.sleep(0.1)
                pass
            timer_send.change(2,3)
            # Waiting for some processus ask for receive the spikes
            for source in source_sending:
                # receive list ids
                size_list = np.empty(1, dtype='i')
                comm.Recv([size_list, 1, MPI.INT], source=source, tag=0, status=status_)
                list_id = np.empty(size_list, dtype='i')
                comm.Recv([list_id, size_list, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
                # Select the good spike train and send it
                # logger.info(" TVB to Nest:"+str(data))
                logger.info("rank "+str(source)+" lits_id "+str(list_id))
                data = []
                shape = []
                for i in list_id:
                    shape += [buffer_spike[0][i-id_first_spike_detector].shape[0]]
                    data += [buffer_spike[0][i-id_first_spike_detector]]
                send_shape = np.array(np.concatenate(([np.sum(shape)],shape)), dtype='i')
                # firstly send the size of the spikes train
                comm.Send([send_shape, MPI.INT], dest=status_.Get_source(), tag=list_id[0])
                # secondly send the spikes train
                data = np.concatenate(data).astype('d')
                comm.Send([data, MPI.DOUBLE], dest=source, tag=list_id[0])
            logger.info(" end sending:")
            timer_send.stop(3)
        elif  status_.Get_tag() == 1:
            # ending the update of the all the spike train from one processus
            logger.info(" TVB to Nest end sending ")
            with lock_status:
                if status_data[0] != 2:
                    status_data[0] = 1
        elif status_.Get_tag() == 2:
            logger.info(" TVB to Nest end simulation ")
            with lock_status:
                status_data[0] = 2
            break
        else:
            raise Exception("bad mpi tag : "+str(status_.Get_tag()))
    timer_send.start(0)
    logger.info('communication disconnect')
    comm.Disconnect()
    logger.info('end thread')
    timer_send.stop(0)
    timer_send.save(path_config+'/../../'+logger.name+'.npy')
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
    timer_receive = Timer(6,100000)
    timer_receive.start(0)
    # Open the MPI port connection
    status_ = MPI.Status()
    source_sending = np.arange(0,comm.Get_remote_size(),1)# list of all the process for the commmunication
    timer_receive.stop(0)
    while True: # FAT END POINT
        # Send to all the confirmation of the processus can send data
        requests=[]
        logger.info(" TVB to Nest: wait receive ")
        timer_receive.start(1)
        for source in source_sending:
            requests.append(comm.isend(True,dest=source,tag=0))
        MPI.Request.Waitall(requests)
        timer_receive.change(1,2)
        logger.info(" TVB to Nest: receive all")
        # get the starting and ending time of the simulation to translate
        time_step = np.empty(2, dtype='d')
        comm.Recv([time_step, 2, MPI.DOUBLE], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        logger.info(" TVB to Nest: get time_step "+str(time_step)+" status : " + str(status_.Get_tag()))
        timer_receive.stop(2)
        if status_.Get_tag() == 0:
            timer_receive.start(3)
            #  Get the size of the data
            size = np.empty(1, dtype='i')
            comm.Recv([size, 1, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
            #  Get the rate
            rate = np.empty(size[0], dtype='d')
            comm.Recv([rate, size[0], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)
            timer_receive.change(3,4)
            spike_generate = generator.generate_spike(0,time_step,rate)
            timer_receive.change(4,5)
            # Wait for lock to be set to False
            while status_data[0] == 1 and status_data[0] == 2:
                time.sleep(0.1)
                pass
            timer_receive.stop(5)
            # Set lock to true and put the data in the shared buffer
            buffer_spike[0] = spike_generate
            with lock_status:
                status_data[0] = 0
        elif status_.Get_tag() == 1:
            with lock_status:
                status_data[0] = 2
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))
    timer_receive.start(0)
    logger.info('communication disconnect')
    comm.Disconnect()
    logger.info('end thread')
    timer_receive.stop(0)
    timer_receive.save(path_config+'/../../'+logger.name+'.npy')
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

    timer_master = Timer(1,10)
    timer_master.start(0)
    # Parse arguments
    path_config = sys.argv[1]
    id_first_spike_detector = int(sys.argv[2])
    nb_spike_generator = int(sys.argv[3])
    TVB_config = sys.argv[4]


    # object for analysing data
    with open(path_config+'/../../parameter.json') as f:
        parameters = json.load(f)
    param = parameters['param_TR_tvb_to_nest']
    generator = generate_data(path_config+'/../../log/',nb_spike_generator,param)
    log_level = param['level_log']
    logger_master = create_logger(path_config, 'tvb_to_nest_master'+str(id_first_spike_detector), log_level)

    # variable for communication between thread
    status_data=[0]
    initialisation =np.load(param['init'])
    buffer_spike=[initialisation]

    ### Create Com objects for communications
    info = MPI.INFO_NULL
    root = 0
        
    ##############################################
    # Create the port, file and set unlock for sender
    logger_master.info('Translate SEND: before open_port')
    port_send = MPI.Open_port(info)  # open a NEW port
    logger_master.info('Translate SEND: after open_port : '+port_send)
    path_to_files_sends = []
    path_to_files_sends_unlock = []
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
    logger_master.info('Translate SEND: path_file: ' + path_to_files_send)

    ##############################################
    #  Create the port, file and set unlock for receiver       
    logger_master.info('Translate RECEIVE: before open_port')
    port_receive = MPI.Open_port(info)
    logger_master.info('Translate RECEIVE: after open_port '+port_receive)
        
    # Write file configuration of the port
    path_to_files_receive = path_config + TVB_config
    logger_master.info('Translate RECEIVE: path_file: ' + path_to_files_receive)
    fport_receive = open(path_to_files_receive, "w+")
    fport_receive.write(port_receive)
    fport_receive.close()
    pathlib.Path(path_to_files_receive + ".unlock").touch()

    ############################################
    timer_master.change(0,0)
    # accept connections
    logger_master.info('Translate SEND: before Accepted: '+ str([port_send, info, root]))
    comm_send = MPI.COMM_WORLD.Accept(port_send, info, root)
    logger_master.info('Translate SEND: Accepted')
        
    logger_master.info('Translate RECEIVE: before accept: '+ str([port_receive, info, root]))
    comm_receive = MPI.COMM_WORLD.Accept(port_receive, info, root)
    logger_master.info('Translate RECEIVE: after accept')
    ##############################################
    timer_master.change(0,0)

    logger_send = create_logger(path_config, 'tvb_to_nest_send'+str(id_first_spike_detector), log_level)
    logger_receive = create_logger(path_config, 'tvb_to_nest_receive'+str(id_first_spike_detector), log_level)
    # create the thread for receive and send data
    th_send = Thread(target=send, args=(logger_send,id_first_spike_detector,status_data,buffer_spike, comm_send))
    th_receive = Thread(target=receive, args=(logger_receive,generator,status_data,buffer_spike, comm_receive ))

    # start the threads
    # FAT END POINT
    logger_master.info('Start thread')
    timer_master.change(0,0)
    th_receive.start()
    th_send.start()
    th_receive.join()
    th_send.join()
    logger_master.info('thread join')
    timer_master.change(0,0)
    MPI.Close_port(port_send)
    MPI.Close_port(port_receive)
    logger_master.info('close communicator')
    MPI.Finalize()

    logger_master.info('clean file')
    # Clean up port files and locks
    for path_send in path_to_files_sends :
        os.remove(path_send)
    os.remove(path_to_files_receive)
    logger_master.info('end')
    timer_master.stop(0)
    timer_master.save(path_config+'/../../'+logger_master.name+'.npy')
