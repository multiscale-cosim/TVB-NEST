import numpy as np
import os
from mpi4py import MPI
from threading import Thread, Lock
from nest_elephant_tvb.simulation.file_translation.science_nest_to_tvb import store_data,analyse_data

lock_status=Lock() # locker for manage the transfer of data from thread

def receive(path,file_spike_detector,store,status_data,buffer):
    '''
    the receive part of the translator
    :param path: folder which will contain the configuration file
    :param file_spike_detector: the relative path which contains the txt file
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    # Open the MPI port connection
    # print("Receive : Waiting for port details");sys.stdout.flush()
    info = MPI.INFO_NULL
    root=0
    port = MPI.Open_port(info)
    # Write file configuration of the port
    path_to_files = path + file_spike_detector
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    # Wait until connection
    # print('Receive : wait connection '+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    # print('Receive : connect to '+port);sys.stdout.flush()

    status_ = MPI.Status() # status of the different message
    source_sending = np.arange(0,comm.Get_remote_size(),1) # list of all the process for the commmunication
    count=0
    while True:
        # send the confirmation of the processus can send data
        requests=[]
        # print("######### Nest to TVB : wait all");sys.stdout.flush()
        for source in source_sending:
            requests.append(comm.Isend([np.array(True,dtype='b'),MPI.BOOL],dest=source,tag=0))
        MPI.Request.Waitall(requests)

        # print("######### Nest to TVB : start to receive");sys.stdout.flush()
        #  Get the data/ spike
        data = np.empty(2, dtype='d')
        count_ending=0
        while count_ending !=len(source_sending):
            comm.Recv([data,2, MPI.DOUBLE],source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG,status=status_)
            if status_.Get_tag() == 1:
                # print("######### Nest to TVB : receive " + str(count_ending)); sys.stdout.flush()
                count_ending+=1
            elif status_.Get_tag() == 0:
                store.add_spikes(count,data)
            else:
                break

        if count_ending !=len(source_sending):
            break
        # wait until the data can be send to the sender thread
        while(status_data[0]):
            pass
        with lock_status:
            status_data[0]=True
        buffer[0]=store.return_data()
        count+=1

    # print('Receive : ending');sys.stdout.flush()
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    # print('Receive : exit');sys.stdout.flush()

def send(path,TVB_config,analyse,status_data,buffer):
    '''
    the sending part of the translator
    :param path:  folder which will contain the configuration file
    :param TVB_config:  the relative path which contains the txt file
    :param analyse ; analyse object to transform spikes to state variable
    :param status_data: the status of the buffer (SHARED between thread)
    :param buffer: the buffer which contains the data (SHARED between thread)
    :return:
    '''
    # Open the MPI port connection
    # print("Send : Waiting for port details");sys.stdout.flush()
    info = MPI.INFO_NULL
    root=0
    port = MPI.Open_port(info)
    # Write file configuration of the port
    path_to_files = path + TVB_config
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    # print('Send : wait connection '+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    # print('Send : connect to '+port);sys.stdout.flush()

    count=0
    status_ = MPI.Status()
    while True:
        # wait until the translator accept the connections
        accept = False
        # print("######### Nest to TVB : wait to send " );sys.stdout.flush()
        while not accept:
            req = comm.irecv(source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG)
            accept = req.wait(status_)

        # print("######### Nest to TVB : send data " );sys.stdout.flush()
        if status_.Get_tag() == 0:
            # send the rate when there ready
            while(not status_data[0]):
                pass
            times,data=analyse.analyse(count,buffer[0])
            print("######### Nest to TVB : send data :"+str(np.sum(data)) );sys.stdout.flush()
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
            #TODO testing
            break
        count+=1

    # print('Send : ending');sys.stdout.flush()
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    # print('Send : exit')


if __name__ == "__main__":
    import sys
    print(sys.argv);sys.stdout.flush()
    if len(sys.argv)==7:
        path_folder_config = sys.argv[1]
        file_spike_detector = sys.argv[2]
        TVB_recev_file = sys.argv[3]
        dt = float(sys.argv[4])
        delay_min = float(sys.argv[5])
        width = float(sys.argv[6])

        # variable for communication between thread
        status_data=[False] # status of the buffer
        buffer=[np.zeros((int(delay_min/dt),1))] # buffer of the rate to send it

        # object for analysing data
        store=store_data(buffer[0].shape,delay_min,dt)
        analyse = analyse_data(int(width/dt), delay_min)

        # create the thread for receive and send data
        th_receive = Thread(target=receive, args=(path_folder_config,file_spike_detector,store,status_data,buffer))
        th_send = Thread(target=send, args=(path_folder_config,TVB_recev_file,analyse,status_data,buffer))

        # start the threads
        th_receive.start()
        th_send.start()
        th_receive.join()
        th_send.join()
        MPI.Finalize()
    else:
        print('missing argument')

