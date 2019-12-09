import numpy as np
import os
from mpi4py import MPI
import copy
import time
from threading import Thread, Lock
#from rate_spike import rates_to_spikes

lock_status=Lock()

# Can be changed to the function we had with elephant, this is just a toy function
def rates_to_spikes(rates,t_start,t_stop):
    time = t_start + np.random.rand(rates) * (t_stop-t_start)
    time = np.around(np.sort(np.array(time)), decimals=1)
    return time

#Send to NEST.
#After connect, NEST sends the time of start and then receives continuously single
#doubles with the tag 0 until a message with tag 1 is received.
def send(path,id_spike_generator,dt,delay_min,status_data,buffer):
    #Start communication channels
    # path_to_files = "/home/kusch/Documents/project/co_simulation/cosim_TVB_NEST/nest-io/pynest/examples/"
    # path_to_files = "/home/kusch/Documents/project/co_simulation/cosim_TVB_NEST/translator/test/config_mpi/" + nb_spike_detector + ".txt"
    path_to_files = path + id_spike_generator + ".txt"
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
    sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('connect to '+port)
    #test one rate
    status_ = MPI.Status()
    current_step = np.empty(1, dtype='d')
    starting = 1
    while True:
        comm.Recv([current_step, 1, MPI.DOUBLE], source=0, tag=MPI.ANY_TAG, status=status_)
        if current_step[0] < starting:
            data = np.array([0],dtype='d')
            comm.Send([data, MPI.DOUBLE], dest=0, tag=1)
            sys.stdout.flush()
        else:
            if status_.Get_tag() == 0:
                while (not status_data[0]):
                    pass
                # Go through all rates
                for rate in buffer[0]:
                    data = rates_to_spikes(rate, starting, starting + (delay_min/len(buffer[0])))
                    for time in data:
                        comm.Send([time, MPI.DOUBLE], dest=0, tag=0)
                        print(" send data ", time)
                comm.Send([time, MPI.DOUBLE], dest=0, tag=1)
                print(" ending", time)
                sys.stdout.flush();
                starting += delay_min;
                with lock_status:
                    print("status false")
                    status_data[0] = False
            else:
                comm.Disconnect()
                comm = MPI.COMM_WORLD.Accept(port, info, root)

    comm.Disconnect()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('exit');
    MPI.Finalize()

#Receive from TVB
#After connect TVB starts sending rates with tag 0.
#When TVB sends a message with tag 1 it indicates it finished this cycle.
#Then, the received rate is stored in the buffer and the status data flag is set to True
#Afterwards, this thread waits again for a
def receive(path,TVB_config,status_data,buffer):
    # Start communication channels
    path_to_files = path + TVB_config + ".txt"
    # For TVB
    # Init connection
    print("Waiting for port details")
    info = MPI.INFO_NULL
    root = 0
    port = MPI.Open_port(info)
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    print('wait connection ' + port)
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('connect to ' + port)
    # test one rate
    status_ = MPI.Status()
    current_step = np.empty(1, dtype='d')
    starting = 0
    while True:
        data = np.empty(1, dtype='d')
        hist = np.zeros(buffer[0].shape)
        comm.Recv([data, 1, MPI.DOUBLE], source=0, tag=MPI.ANY_TAG, status=status_)
        while status_.Get_tag() == 0:
            print("status ", data[0])
            sys.stdout.flush()
            #Think how to fill the history buffer with rates
            hist[starting] = data[0]
            starting +=1
            comm.Recv([data, 1, MPI.DOUBLE], source=0, tag=MPI.ANY_TAG, status=status_)
        if status_.Get_tag() == 1:
            while (status_data[0]):
                pass
            with lock_status:
                status_data[0] = True
            buffer[0] = copy.copy(hist)
        else:
            break
    print("ending" )
    comm.Send([starting, MPI.DOUBLE], dest=0, tag=2)
    comm.Disconnect()
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
        th_send = Thread(target=send, args=(path_config,id_spike_detector,dt,delay_min,status_data,buffer ))
        th_receive = Thread(target=receive, args=(path_config,TVB_config,status_data,buffer ))
        th_receive.start()
        th_send.start()
        th_receive.join()
        th_send.join()
    else:
        print('missing argument')

