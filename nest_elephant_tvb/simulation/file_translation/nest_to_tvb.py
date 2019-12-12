import numpy as np
import os
from mpi4py import MPI
import copy
import time
from threading import Thread, Lock

lock_status=Lock()

def receive(path,id_spike_detector,dt,delay_min,status_data,buffer):
    starting=0.0
    #Start communication channels
    path_to_files = path + id_spike_detector + ".txt"
    #For NEST
    # Init connection
    print("Waiting for port details")
    info = MPI.INFO_NULL
    root=0
    port = MPI.Open_port(info)
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    print('wait connection '+port)
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('connect to '+port)
    #test one rate
    status_ = MPI.Status()
    sys.stdout.flush()
    while(True):
        data = np.empty(2, dtype='d')
        data[0]=starting
        hist = np.zeros(buffer[0].shape)
        comm.Send([data[0], MPI.DOUBLE], dest=0, tag=0)
        comm.Recv([data, 2, MPI.DOUBLE], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        while status_.Get_tag() == 0:
            sys.stdout.flush()
            hist[int((data[1]-starting)/dt)]+=1
            comm.Recv([data,2, MPI.DOUBLE],source=status_.Get_source(),tag=MPI.ANY_TAG,status=status_)
        if status_.Get_tag() == 1:
            while(status_data[0]):
                pass
            with lock_status:
                status_data[0]=True
            buffer[0]=copy.copy(hist)
            starting+=delay_min
        else:
            break
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('exit')
    MPI.Finalize()

def send(path,TVB_config,status_data,buffer):
    #Start communication channels
    path_to_files = path + TVB_config + ".txt"
    #For TVB
    # Init connection
    print("Waiting for port details")
    info = MPI.INFO_NULL
    root=0
    port = MPI.Open_port(info)
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    print('wait connection '+port)
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('connect to '+port)
    #test one rate
    status_ = MPI.Status()
    sys.stdout.flush()
    while(True):
        accept = np.empty(1, dtype='b')
        comm.Recv([accept,1, MPI.BOOL],source=MPI.ANY_SOURCE,tag=MPI.ANY_TAG,status=status_)
        if status_.Get_tag() == 0:
            while(not status_data[0]):
                pass
            size = np.array(int(buffer[0].shape[0]),dtype='i')
            comm.Send([size,MPI.INT],dest=status_.Get_source(),tag=0)
            sys.stdout.flush()
            comm.Send([buffer[0], MPI.DOUBLE], dest=status_.Get_source(), tag=0)
            with lock_status:
                print("status false")
                status_data[0]=False
        else:
            comm.Disconnect()
            comm = MPI.COMM_WORLD.Accept(port, info, root)
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('exit');
    MPI.Finalize()


if __name__ == "__main__":
    import sys
    if len(sys.argv)==6:
        path_config = sys.argv[1]
        id_spike_detector = sys.argv[2]
        TVB_config = sys.argv[3]
        dt = float(sys.argv[4])
        delay_min =  float(sys.argv[5])
        status_data=[False]
        buffer=[np.zeros((int(delay_min/dt),1))]
        th_receive = Thread(target=receive, args=(path_config,id_spike_detector,dt,delay_min,status_data,buffer ))
        th_send = Thread(target=send, args=(path_config,TVB_config,status_data,buffer ))
        th_receive.start()
        th_send.start()
        th_receive.join()
        th_send.join()
    else:
        print('missing argument')

