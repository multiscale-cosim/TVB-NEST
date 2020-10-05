#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
import os
import json
import time
import pathlib
from mpi4py import MPI
from threading import Thread, Lock
import logging
from nest_elephant_tvb.translation.science_nest_to_tvb import store_data,analyse_data
from timer.Timer import Timer

lock_status=Lock() # locker for manage the transfer of data from thread

def receive(logger,store,status_data,buffer, comm):
    '''
    the receive part of the translator
    :param logger : logger fro the thread
    :param store : object for store the data before analysis
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    timer_receive = Timer(5,1000)
    timer_receive.start(0)
    # initialise variables for the loop
    status_ = MPI.Status() # status of the different message
    source_sending = np.arange(0,comm.Get_remote_size(),1) # list of all the process for the commmunication
    check = np.empty(1,dtype='b')
    count=0
    timer_receive.stop(0)
    while True: # FAT END POINT
        # send the confirmation of the process can send data
        requests=[]
        logger.info(" Nest to TVB : wait all")
        timer_receive.start(1)
        for source in source_sending:
            comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
        timer_receive.stop(1)

        if status_.Get_tag() == 0:
            timer_receive.start(2)
            wait = 0
            logger.info(" Nest to TVB : start to receive")
            #  Get the data/ spike
            for source in source_sending:
                comm.Send([np.array(True,dtype='b'),MPI.BOOL],dest=source,tag=0)
                shape = np.empty(1, dtype='i')
                comm.Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                if wait == 0:
                    timer_receive.change(2,3)
                data = np.empty(shape[0], dtype='d')
                comm.Recv([data, shape[0], MPI.DOUBLE], source=source, tag=0, status=status_)
                store.add_spikes(count,data)
            timer_receive.change(3,4)
            while status_data[0] != 1 and status_data[0] != 2: # FAT END POINT
                time.sleep(0.1)
                pass
            # wait until the data can be send to the sender thread
            # Set lock to true and put the data in the shared buffer
            buffer[0] = store.return_data()
            with lock_status: # FAT END POINT
                if status_data[0] != 2:
                    status_data[0] = 0
            timer_receive.stop(4)
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
    timer_receive.start(0)
    logger.info('communication disconnect')
    comm.Disconnect()
    logger.info('end thread')
    timer_receive.stop(0)
    timer_receive.save(path+logger.name+'.npy')
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
    timer_send = Timer(5,1000)
    timer_send.start(0)
    count=0
    status_ = MPI.Status()
    timer_send.stop(0)
    while True: # FAT END POINT
        # wait until the translator accept the connections
        accept = False
        logger.info("Nest to TVB : wait to send " )
        timer_send.start(1)
        while not accept:
            req = comm.irecv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG)
            accept = req.wait(status_)
        timer_send.stop(1)
        logger.info(" Nest to TVB : send data status : " +str(status_.Get_tag()))
        if status_.Get_tag() == 0:
            # send the rate when there ready
            timer_send.start(2)
            while status_data[0] != 0: # FAT END POINT
                time.sleep(0.1)
                pass
            timer_send.change(2,3)
            times,data=analyse.analyse(count,buffer[0])
            timer_send.change(3,4)
            logger.info("Nest to TVB : send data :"+str(np.sum(data)) )
            # time of stating and ending step
            comm.Send([times, MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            # send the size of the rate
            size = np.array(int(data.shape[0]),dtype='i')
            comm.Send([size,MPI.INT], dest=status_.Get_source(), tag=0)
            # send the rates
            comm.Send([data,MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            with lock_status:
                if status_data[0] != 2:
                    status_data[0] = 1
            timer_send.stop(4)
        elif status_.Get_tag() == 1:
            # disconnect when everything is ending
            with lock_status:
                status_data[0] = 2
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))
        count+=1
    timer_send.start(0)
    logger.info('communication disconnect')
    comm.Disconnect()
    logger.info('end thread')
    timer_send.stop(0)
    timer_send.save(path+logger.name+'.npy')
    return

def create_logger(path,name, log_level):
    # Configure logger
    logger = logging.getLogger(name)
    fh = logging.FileHandler(path+'/log/'+name+'.log')
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
    from timer.Timer import Timer
    timer_main = Timer(1,10)
    timer_main.start(0)

    if len(sys.argv)!=4:
        print('incorrect number of arguments')
        exit(1)

    path = sys.argv[1]
    file_spike_detector = sys.argv[2]
    TVB_recev_file = sys.argv[3]

    # take the parameters and instantiate objects for analysing data
    with open(path+'/parameter.json') as f:
        parameters = json.load(f)
    param = parameters['param_TR_nest_to_tvb']
    store = store_data(path+'/log/',param)
    analyse = analyse_data(path+'/log/',param)
    level_log = param['level_log']
    id_spike_detector = os.path.splitext(os.path.basename(path+file_spike_detector))[0]
    logger_master = create_logger(path, 'nest_to_tvb_master'+str(id_spike_detector), level_log)

    # variable for communication between thread
    status_data=[0] # status of the buffer
    initialisation =np.load(param['init']) # initialisation value
    buffer=[initialisation] # buffer of the rate to send it

    ############
    # Open the MPI port connection for receiver
    info = MPI.INFO_NULL
    root=0

    logger_master.info('Translate Receive: before open_port')
    port_receive = MPI.Open_port(info)
    logger_master.info('Translate Receive: after open_port: '+port_receive)
    # Write file configuration of the port
    path_to_files_receive = path + file_spike_detector
    fport = open(path_to_files_receive, "w+")
    fport.write(port_receive)
    fport.close()
    pathlib.Path(path_to_files_receive+'.unlock').touch()
    logger_master.info('Translate Receive: path_file: ' + path_to_files_receive)
    #########################

    ######################
    # open for for the sender
    logger_master.info('Translate SEND: before open_port')
    port_send = MPI.Open_port(info)
    logger_master.info('Translate SEND: after open_port : '+port_send)
    # Write file configuration of the port
    path_to_files_send = path + TVB_recev_file
    fport = open(path_to_files_send, "w+")
    fport.write(port_send)
    fport.close()
    pathlib.Path(path_to_files_send+'.unlock').touch()
    logger_master.info('Translate SEND: path_file: ' + path_to_files_send);sys.stdout.flush()
    ##############
    timer_main.change(0,0)
    #############
    # Wait until connection
    logger_master.info('Waiting communication')
    comm_receiver = MPI.COMM_WORLD.Accept(port_receive, info, root)
    comm_sender = MPI.COMM_WORLD.Accept(port_send, info, root)
    logger_master.info('get communication and start thread')
    #############
    timer_main.change(0,0)

    logger_receive = create_logger(path, 'nest_to_tvb_receive'+str(id_spike_detector), level_log)
    logger_send = create_logger(path, 'nest_to_tvb_send'+str(id_spike_detector), level_log)
    # create the thread for receive and send data
    th_receive = Thread(target=receive, args=(logger_receive,store,status_data,buffer, comm_receiver))
    th_send = Thread(target=send, args=(logger_send,analyse,status_data,buffer, comm_sender))

    # start the threads
    # FAT END POINT
    logger_master.info('Start thread')
    timer_main.change(0,0)
    th_receive.start()
    th_send.start()
    th_receive.join()
    th_send.join()
    timer_main.change(0,0)
    logger_master.info('thread join')

    # close port
    MPI.Close_port(port_send)
    MPI.Close_port(port_receive)
    logger_master.info('close communicator')

    # finalise MPI
    MPI.Finalize()

    logger_master.info('clean file')
    os.remove(path_to_files_receive)
    os.remove(path_to_files_send)
    logger_master.info('end')
    timer_main.stop(0)
    timer_main.save(path+logger_master.name+'.npy')