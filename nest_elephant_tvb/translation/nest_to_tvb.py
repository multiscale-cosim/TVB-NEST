#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import os
import json
import logging

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
    
    
    ############ NEW Code: old logging code copied here for better overview
    level_log = param['level_log']
    id_spike_detector = os.path.splitext(os.path.basename(path+file_spike_detector))[0]
    logger_master = create_logger(path, 'nest_to_tvb_master'+str(id_spike_detector), level_log)
    logger_receive = create_logger(path, 'nest_to_tvb_receive'+str(id_spike_detector), level_log)
    logger_send = create_logger(path, 'nest_to_tvb_send'+str(id_spike_detector), level_log)
    ############# NEW Code end
    
    
    ############ NEW Code: FAT END POINT for MPI and new connections
    ### contains all MPI connection stuff for proper encapsulation
    ### TODO: make this a proper interface
    import nest_elephant_tvb.translation.FatEndPoint as FEP
    path_to_files_receive = path + file_spike_detector # TODO: use proper path operations
    path_to_files_send = path + TVB_recev_file
    comm, comm_receiver, port_receive, comm_sender, port_send = FEP.make_connections(path_to_files_receive, path_to_files_send, logger_master)
    ############# NEW Code end
    
    
    ############ NEW Code: removed threads, used MPI ranks...
    ### TODO: encapsulate loggers
    ### kept all logging stuff here for now to have them in one place
    import nest_elephant_tvb.translation.mpi_translator as mt
    loggers = [logger_master, logger_receive, logger_send] # list of all the loggers
    mt.init(path, param, comm, comm_receiver, comm_sender, loggers)
    ############ NEW Code end
    
    
    ############ NEW Code: FAT END POINT for MPI and new connections
    ### contains all MPI connection stuff for proper encapsulation
    ### TODO: make this a proper interface
    FEP.close_and_finalize(port_send, port_receive,logger_master)
    ############# NEW Code end
    
    logger_master.info('clean file')
    os.remove(path_to_files_receive)
    os.remove(path_to_files_send)
    logger_master.info('end')
