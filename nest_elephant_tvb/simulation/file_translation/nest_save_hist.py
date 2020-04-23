import numpy as np
from mpi4py import MPI
from threading import Thread
from nest_elephant_tvb.simulation.file_translation.nest_to_tvb import receive,store_data,lock_status,logging

def save(path,nb_step,step_save,status_data,buffer):
    '''
    WARNING never ending
    :param path:  folder which will contain the configuration file
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    logger = logging.getLogger('nest_save')
    fh = logging.FileHandler(path+'/../../log/nest_save.log')
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

    buffer_save = None

    count=0
    while count<nb_step:
        logger.info("Nest save : save "+str(count))
        # send the rate when there ready
        while(not status_data[0]):
            pass
        if buffer_save is None:
            logger.info("buffer 1 : "+str(count))
            buffer_save = buffer[0]
        elif count % step_save == 0:
            logger.info("buffer 2 : "+str(count))
            buffer_save = np.concatenate((buffer_save,buffer[0]))
            np.save(path+"_"+str(count)+".npy",buffer_save)
            buffer_save = None
        else:
            logger.info("buffer 3 : "+str(count))
            buffer_save = np.concatenate((buffer_save,buffer[0]))
        with lock_status:
            status_data[0]=False
        count+=1
    logger.info('Save : ending');sys.stdout.flush()
    if buffer_save is not None:
        np.save(path + str(count) + ".npy", buffer_save)


if __name__ == "__main__":
    import sys
    if len(sys.argv)==5:
        path_folder_config = sys.argv[1]
        file_spike_detector = sys.argv[2]
        path_folder_save = sys.argv[3]
        end = float(sys.argv[4])

        # object for analysing data
        sys.path.append(path_folder_config)
        from parameter import param_record_MPI as param
        sys.path.remove(path_folder_config)
        time_synch = param['synch']
        nb_step = np.ceil(end/time_synch)
        step_save = param['save_step']
        level_log = param['level_log']


        # variable for communication between thread
        status_data=[False] # status of the buffer
        buffer=[np.array([])]

        # object for analysing data
        store=store_data(path_folder_config,param)

        # create the thread for receive and send data
        th_receive = Thread(target=receive, args=(path_folder_config,level_log,file_spike_detector,store,status_data,buffer))
        th_save = Thread(target=save, args=(path_folder_save,nb_step,step_save,status_data,buffer))

        # start the threads
        th_receive.start()
        th_save.start()
        th_receive.join()
        th_save.join()
        MPI.Finalize()
    else:
        print('missing argument')

