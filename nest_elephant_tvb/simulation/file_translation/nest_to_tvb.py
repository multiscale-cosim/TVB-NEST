import numpy as np
import os
from mpi4py import MPI
from threading import Thread, Lock
from nest_elephant_tvb.simulation.file_translation.science_nest_to_tvb import store_data,analyse_data
import logging

lock_status=Lock() # locker for manage the transfer of data from thread

def receive(path,level_log,file_spike_detector,store,status_data,buffer):
    '''
    the receive part of the translator
    :param path: folder which will contain the configuration file
    :param file_spike_detector: the relative path which contains the txt file
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    # Configuration logger
    logger = logging.getLogger('nest_to_tvb_receive')
    fh = logging.FileHandler(path+'/log/nest_to_tvb_receive.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if level_log == 0:
        fh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif  level_log == 1:
        fh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif  level_log == 2:
        fh.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    elif  level_log == 3:
        fh.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    elif  level_log == 4:
        fh.setLevel(logging.CRITICAL)
        logger.setLevel(logging.CRITICAL)

    # Open the MPI port connection
    logger.info("Receive : Waiting for port details")
    info = MPI.INFO_NULL
    root=0
    port = MPI.Open_port(info)
    # Write file configuration of the port
    path_to_files = path + file_spike_detector
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    # Wait until connection
    logger.info('Receive : wait connection '+port)
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    logger.info('Receive : connect to '+port)

    status_ = MPI.Status() # status of the different message
    source_sending = np.arange(0,comm.Get_remote_size(),1) # list of all the process for the commmunication
    check = np.empty(1,dtype='b')
    count=0
    while True:
        # send the confirmation of the processus can send data
        requests=[]
        logger.info(" Nest to TVB : wait all")
        for source in source_sending:
            comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)

        if status_.Get_tag() == 0:
            logger.info(" Nest to TVB : start to receive")
            #  Get the data/ spike
            for source in source_sending:
                comm.Send([np.array(True,dtype='b'),MPI.BOOL],dest=source,tag=0)
                shape = np.empty(1, dtype='i')
                comm.Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                data = np.empty(shape[0], dtype='d')
                comm.Recv([data, shape[0], MPI.DOUBLE], source=source, tag=0, status=status_)
                store.add_spikes(count,data)
            while (status_data[0]):
                pass
            # wait until the data can be send to the sender thread
            # Set lock to true and put the data in the shared buffer
            buffer[0] = store.return_data()
            with lock_status:
                status_data[0] = True
        elif status_.Get_tag() == 1:
            logger.info("Nest to TVB : receive end " + str(count))
            count += 1
        elif status_.Get_tag() == 2:
            with lock_status:
                status_data[0] = True
            logger.info("end simulation")
            break
        else:
            raise Exception("bad mpi tag"+str(status_.Get_tag()))

    logger.info('Receive : ending')
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    logger.info('Receive : exit')

def send(path,level_log,TVB_config,analyse,status_data,buffer):
    '''
    the sending part of the translator
    :param path:  folder which will contain the configuration file
    :param TVB_config:  the relative path which contains the txt file
    :param analyse ; analyse object to transform spikes to state variable
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    # Configuration logger
    logger = logging.getLogger('nest_to_tvb_send')
    fh = logging.FileHandler(path+'/log/nest_to_tvb_send.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if level_log == 0:
        fh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif  level_log == 1:
        fh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif  level_log == 2:
        fh.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    elif  level_log == 3:
        fh.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    elif  level_log == 4:
        fh.setLevel(logging.CRITICAL)
        logger.setLevel(logging.CRITICAL)

    # Open the MPI port connection
    logger.info("Send : Waiting for port details")
    info = MPI.INFO_NULL
    root=0
    port = MPI.Open_port(info)
    # Write file configuration of the port
    path_to_files = path + TVB_config
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    logger.info('Send : wait connection '+port)
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    logger.info('Send : connect to '+port)

    count=0
    status_ = MPI.Status()
    while True:
        # wait until the translator accept the connections
        accept = False
        logger.info("Nest to TVB : wait to send " )
        while not accept:
            req = comm.irecv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG)
            accept = req.wait(status_)

        logger.info(" Nest to TVB : send data " )
        if status_.Get_tag() == 0:
            # send the rate when there ready
            while(not status_data[0]):
                pass
            times,data=analyse.analyse(count,buffer[0])
            logger.info("Nest to TVB : send data :"+str(np.sum(data)) )
            # time of stating and ending step
            comm.Send([times, MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            # send the size of the rate
            size = np.array(int(data.shape[0]),dtype='i')
            comm.Send([size,MPI.INT], dest=status_.Get_source(), tag=0)
            # send the rates
            comm.Send([data,MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            with lock_status:
                status_data[0]=False
        else:
            # disconnect when everything is ending
            with lock_status:
                status_data[0]=False
            break
        count+=1

    logger.info('Send : ending')
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    logger.info('Send : exit')


if __name__ == "__main__":
    import sys
    if len(sys.argv)==4:
        path_folder_config = sys.argv[1]
        file_spike_detector = sys.argv[2]
        TVB_recev_file = sys.argv[3]

        # object for analysing data
        sys.path.append(path_folder_config)
        from parameter import param_TR_nest_to_tvb as param
        sys.path.remove(path_folder_config)
        store=store_data(path_folder_config,param)
        analyse = analyse_data(path_folder_config,param)

        # variable for communication between thread
        status_data=[True] # status of the buffer
        initialisation =np.load(param['init']) # initialisation value
        buffer=[initialisation] # buffer of the rate to send it
        level_log = param['level_log']

        # create the thread for receive and send data
        th_receive = Thread(target=receive, args=(path_folder_config,level_log,file_spike_detector,store,status_data,buffer))
        th_send = Thread(target=send, args=(path_folder_config,level_log,TVB_recev_file,analyse,status_data,buffer))

        # start the threads
        th_receive.start()
        th_send.start()
        th_receive.join()
        th_send.join()
        MPI.Finalize()
    else:
        print('missing argument')

