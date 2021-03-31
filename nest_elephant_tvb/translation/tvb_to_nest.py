#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import os
import json
import logging
import sys

import nest_elephant_tvb.translation.RichEndPoint as REP
import nest_elephant_tvb.translation.transformer_tvb_nest as ttn

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

    ############ Step 1: all argument parsing stuff
    ### TODO: cleanup and proper parsing.
    if len(sys.argv)!=5:
        print('missing argument')
        exit (1)
    path_config = sys.argv[1]
    id_first_spike_detector = int(sys.argv[2])
    nb_spike_generator = int(sys.argv[3])
    TVB_config = sys.argv[4]
    # take the parameters and instantiate objects for analysing data
    with open(path_config+'/../../parameter.json') as f:
        parameters = json.load(f)
    param = parameters['param_TR_tvb_to_nest']
    ############
    
    ############ Step 2: init all loggers.
    ### TODO: use proper logging interface 
    ### -> https://github.com/multiscale-cosim/TVB-NEST/tree/master/configuration_manager

    log_level = param['level_log']
    logger_master = create_logger(path_config, 'tvb_to_nest_master'+str(id_first_spike_detector), log_level)
    logger_send = create_logger(path_config, 'tvb_to_nest_send'+str(id_first_spike_detector), log_level)
    logger_receive = create_logger(path_config, 'tvb_to_nest_receive'+str(id_first_spike_detector), log_level)
    ############
    
    ############ Step 3: RichEndPoint -- open MPI connections
    ### TODO: make this a proper interface
    path_to_files_receive = path_config + TVB_config
    path_to_files_send = os.path.join(path_config, str(id_first_spike_detector) + ".txt")
    comm, comm_receiver, port_receive, comm_sender, port_send = REP.make_connections(path_to_files_receive, path_to_files_send, logger_master)
    '''
    # TODO: why is the loop needed, could not see where this is ever reused.
    # TODO: only path/output/0.txt is
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
    ############
    
    ############ Step 4: MPI Transformer, init and start the co-simulation
    ### TODO: encapsulate loggers, kept all logging stuff here for now to have them in one place
    ### TODO: split Transformer its sub-tasks: RichEndPoint, Transformation, Sciences
    ### TODO: looong parameter list. Do this properly after merging with the launcher from Rolando
    loggers = [logger_master, logger_receive, logger_send] # list of all the loggers
    ttn.init(path_config, nb_spike_generator, id_first_spike_detector, param,
            comm, comm_receiver, comm_sender, loggers)
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
