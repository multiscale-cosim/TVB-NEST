#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
import os
from mpi4py import MPI
from tests.test_nest_MPI_threading.helper import create_logger,generate_spike

def input(path,file,nb_mpi,nb_run,time_sim):
    """
    Simulate some random random current
    :param path: the file for the configurations of the connection
    :param file: number of the device and the file connection
    :param nb_mpi: number of mpi of nest
    :param nb_run: the number of run of the simulation (should be more integrate)
    :param time_sim: time of one simulation
    :return:
    """
    logger = create_logger(path,name='input_'+file)
    datas = generate_spike(int(file),nb_run,time_sim)
    #Start communication channels
    path_to_files = path + file +'.txt'
    #For NEST
    # Init connection
    logger.info("Waiting for port details")
    info = MPI.INFO_NULL
    root=0
    port = MPI.Open_port(info)
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    logger.info('wait connection '+port)
    sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    logger.info('connect to '+port)

    #test one rate
    status_ = MPI.Status()
    check = np.empty(1,dtype='b')
    source_sending = np.arange(0,nb_mpi,1) # list of all the process for the communication
    starting = 1
    run_x=0
    while True:
        tag = -1
        for source in source_sending:
            comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
            if tag == -1:
                tag = status_.Get_tag()
            elif tag != status_.Get_tag():
                raise Exception('bad tags')

        logger.info(" start to send")
        logger.info(" status a tag "+str(status_.Get_tag()))
        if tag == 0 :
            # receive list ids
            size_list = np.empty(1, dtype='i')
            shape = np.array(datas[0][run_x],dtype='i')
            data = np.array(datas[1][run_x],dtype='d')
            logger.info("shape data init"+str( data.shape))
            sys.stdout.flush()
            for source in source_sending:
                logger.info(" source :"+str(source))
                comm.Recv([size_list, 1, MPI.INT], source=source, tag=0, status=status_)
                if size_list[0] != 0 :
                    logger.info("size list id"+str(size_list))
                    list_id = np.empty(size_list, dtype='i')
                    comm.Recv([list_id, size_list, MPI.INT], source=status_.Get_source(), tag=0, status=status_)
                    logger.info("id "+str(list_id))
                    data_send = np.concatenate(np.repeat([data],size_list[0]+1,axis=0))
                    logger.info(data_send)
                    send_shape = np.array(np.concatenate([[data_send.shape[0]], np.repeat(shape,size_list[0])]), dtype='i')
                    comm.Send([send_shape, MPI.INT], dest=status_.Get_source(), tag=list_id[0])
                    logger.info("shape data "+str(send_shape))
                    comm.Send([data_send, MPI.DOUBLE], dest=status_.Get_source(), tag=list_id[0])
                    logger.info("send data "+str( data.shape)+" data send "+str(data_send.shape))
            for source in source_sending:
                comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
                logger.info("source "+str(source)+" end run")
            run_x+=1
            starting+=200
        elif(tag == 2):
            logger.info("end simulation")
            logger.info("ending time : "+str(starting))
            break
        else:
            logger.info(tag)
            break
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    logger.info('exit')
    MPI.Finalize()


if __name__ == "__main__":
    import sys
    if len(sys.argv)==6:
        input(sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]))
    else:
        print('missing argument')