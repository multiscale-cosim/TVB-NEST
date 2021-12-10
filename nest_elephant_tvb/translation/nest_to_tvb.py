#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import os
import json
import logging
import sys

import nest_elephant_tvb.translation.RichEndPoint as REP
import nest_elephant_tvb.translation.transformer_nest_tvb as tnt

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
    
    ############ Step 1: all argument parsing stuff
    ### TODO: cleanup and proper parsing.
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
    #############
    
    ############ Step 2: init all loggers.
    ### TODO: use proper logging interface 
    ### -> https://github.com/multiscale-cosim/TVB-NEST/tree/master/configuration_manager
    level_log = param['level_log']
    id_spike_detector = os.path.splitext(os.path.basename(path+file_spike_detector))[0]
    logger_master = create_logger(path, 'nest_to_tvb_master'+str(id_spike_detector), level_log)
    logger_receive = create_logger(path, 'nest_to_tvb_receive'+str(id_spike_detector), level_log)
    logger_send = create_logger(path, 'nest_to_tvb_send'+str(id_spike_detector), level_log)
    #############
    
    ############ Step 3: RichEndPoint -- open MPI connections
    ### TODO: make this a proper interface
    path_to_files_receive = path + file_spike_detector # TODO: use proper path operations
    print(f'DEBUG {__file__}=> path_to_files_receive: {path_to_files_receive}')
    path_to_files_send = path + TVB_recev_file
    print(f'DEBUG {__file__}=> path_to_files_send: {path_to_files_send}')
    comm, comm_receiver, port_receive, comm_sender, port_send = REP.make_connections(path_to_files_receive, path_to_files_send, logger_master)
    #############
    
    ############ Step 4: MPI Transformer, init and start the co-simulation
    ### TODO: encapsulate loggers, kept all logging stuff here for now to have them in one place
    ### TODO: split Transformer its sub-tasks: RichEndPoint, Transformation, Science
    loggers = [logger_master, logger_receive, logger_send] # list of all the loggers
    tnt.init(path, param, comm, comm_receiver, comm_sender, loggers)
    ############
    
    ############ Step 5: RichEndPoint -- close MPI connections
    ### TODO: make this a proper interface
    REP.close_and_finalize(port_send, port_receive,logger_master)
    ############
    
    ############ Step 6: cleanup, delete files
    ### TODO: ugly solution, all MPI ranks want to delete, only the first one can.
    logger_master.info('clean file')
    try:
        os.remove(path_to_files_receive)
        os.remove(path_to_files_send)
    except FileNotFoundError:
        pass 
    logger_master.info('end')
    ############
