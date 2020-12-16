#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
import json
from mpi4py import MPI
from threading import Thread
import pathlib
import time
from nest_elephant_tvb.translation.nest_to_tvb import receive,store_data,lock_status,create_logger

def save(path,logger,nb_step,step_save,status_data,buffer):
    '''
    WARNING never ending
    :param path:  folder which will contain the configuration file
    :param logger : the logger fro the thread
    :param nb_step : number of time for saving data
    :param step_save : number of integration step to save in same time
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    # initialisation variable
    buffer_save = None
    count=0
    while count<nb_step: # FAT END POINT
        logger.info("Nest save : save "+str(count))
        # send the rate when there ready
        while status_data[0] != 0 and status_data[0] != 2: # FAT END POINT
            time.sleep(0.1)
            pass
        if buffer_save is None:
            logger.info("buffer initialise buffer : "+str(count))
            buffer_save = buffer[0]
        elif count % step_save == 0:
            logger.info("buffer save buffer : "+str(count))
            buffer_save = np.concatenate((buffer_save,buffer[0]))
            np.save(path+"_"+str(count)+".npy",buffer_save)
            buffer_save = None
        else:
            logger.info("fill the buffer : "+str(count))
            buffer_save = np.concatenate((buffer_save,buffer[0]))
        with lock_status:
            status_data[0]=1
        count+=1
    logger.info('Save : ending');sys.stdout.flush()
    if buffer_save is not None:
        np.save(path + "_" + str(count) + ".npy", buffer_save)
    return


if __name__ == "__main__":
    import sys
    if len(sys.argv)==5:
        path_folder_config = sys.argv[1]
        file_spike_detector = sys.argv[2]
        path_folder_save = sys.argv[3]
        end = float(sys.argv[4])

        # parameters for the module
        # take the parameters and instantiate objects for analysing data
        with open(path_folder_config+'/parameter.json') as f:
            parameters = json.load(f)
        param = parameters['param_record_MPI']
        time_synch = param['synch']
        nb_step = np.ceil(end/time_synch)
        step_save = param['save_step']
        level_log = param['level_log']
        logger_master = create_logger(path_folder_config, 'nest_to_tvb_master', level_log)

        # variable for communication between thread
        status_data=[1] # status of the buffer
        buffer=[np.array([])]

        # object for analysing data
        store=store_data(path_folder_config,param)

        ############
        # Open the MPI port connection for receiver
        info = MPI.INFO_NULL
        root=0

        logger_master.info('Translate Receive: before open_port')
        port_receive = MPI.Open_port(info)
        logger_master.info('Translate Receive: after open_port')
        # Write file configuration of the port
        path_to_files = path_folder_config + file_spike_detector
        fport = open(path_to_files, "w+")
        fport.write(port_receive)
        fport.close()
        # rename forces that when the file is there it also contains the port
        pathlib.Path(path_to_files+'.unlock').touch()
        logger_master.info('Translate Receive: path_file: ' + path_to_files)
        # Wait until connection
        logger_master.info('Waiting communication')
        comm_receiver = MPI.COMM_WORLD.Accept(port_receive, info, root)
        logger_master.info('get communication and start thread')
        #########################

        # create the thread for receive and save data
        logger_receive = create_logger(path_folder_config, 'nest_to_tvb_receive', level_log)
        logger_save = create_logger(path_folder_config, 'nest_to_tvb_send', level_log)
        th_receive = Thread(target=receive,
                            args=(logger_receive, store, status_data, buffer, comm_receiver))
        th_save = Thread(target=save, args=(path_folder_save,logger_save,nb_step,step_save,status_data,buffer))

        # start the threads
        # FAT END POINT
        logger_master.info('start thread')
        th_receive.start()
        th_save.start()
        th_receive.join()
        th_save.join()
        logger_master.info('join thread')
        MPI.Close_port(port_receive)
        MPI.Finalize()
    else:
        print('missing argument')