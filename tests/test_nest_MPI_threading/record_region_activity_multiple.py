#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
import os
import copy
from mpi4py import MPI
from tests.test_nest_MPI_threading.helper import create_logger

def analyse(path,file,nb_mpi):
    """
    simulate the recorder module
    :param path: the file for the configurations of the connection
    :param file: number of the device and the file connection
    :param nb_mpi: number of mpi rank for testing multi-threading and MPI simulation
    :return:
    """
    data_save = []
    logger = create_logger(path,name='record_'+file)
    # Start communication channels
    path_to_files = path +file+'.txt'
    # For NEST
    # Init connection
    logger.info("Waiting for port details")
    info = MPI.INFO_NULL
    root=0
    port = MPI.Open_port(info)
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    logger.info('wait connection '+port)
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    logger.info('connect to '+port)

    #test one rate
    status_ = MPI.Status()
    check = np.empty(1,dtype='b')
    source_sending = np.arange(0,comm.Get_remote_size(),1) # list of all the process for the commmunication
    while(True):
        comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        logger.info(" start to send")
        logger.info(" status a tag "+str(status_.Get_tag())+" source "+str(status_.Get_source()))
        if status_.Get_tag() == 0:
            for i in range(nb_mpi-1):
                comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=0, status=status_)
            for source in source_sending:
                logger.info("source is "+str(source))
                comm.Send([np.array(True,dtype='b'),MPI.BOOL],dest=source,tag=0)
                shape = np.empty(1, dtype='i')
                comm.Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                logger.info("shape is "+str(shape[0]))
                data = np.empty(shape[0], dtype='d')
                comm.Recv([data, shape[0], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)
                data_save.append(copy.deepcopy(data).reshape(int(shape[0]/3),3))
                logger.info("data is "+str(data))
        elif status_.Get_tag() == 1:
            logger.info("end run")
            pass
        elif status_.Get_tag() ==2:
            for i in range(nb_mpi-1):
                logger.info(" receive ending "+str(i))
                comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
            logger.info("end simulation")
            break
        else:
            logger.info(str(status_.Get_tag()))
            break
    comm.Barrier()
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    logger.info('exit')
    MPI.Finalize()
    np.save(path+'../recording_mpi_'+file+'.npy',data_save,allow_pickle=True)

if __name__ == "__main__":
    import sys
    if len(sys.argv)== 4 :
        analyse(sys.argv[1],sys.argv[2],int(sys.argv[3]))
    else:
        print('missing argument')