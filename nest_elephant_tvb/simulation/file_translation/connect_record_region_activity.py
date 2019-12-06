import numpy as np
import os
import numpy.random as rgn
from mpi4py import MPI

def analyse(path,nb_spike_detector):
    #Start communication channels
    # path_to_files = "/home/kusch/Documents/project/co_simulation/cosim_TVB_NEST/nest-io/pynest/examples/"
    # path_to_files = "/home/kusch/Documents/project/co_simulation/cosim_TVB_NEST/translator/test/config_mpi/" + nb_spike_detector + ".txt"
    path_to_files = path + nb_spike_detector + ".txt"
    #For NEST
    # Init connection
    print(path_to_files)
    print("Waiting for port details")
    fport = open(path_to_files, "r")
    port=fport.readline()
    fport.close()
    print("wait connection "+port)
    comm = MPI.COMM_WORLD.Connect(port)
    print('connect to '+port)
    sys.stdout.flush()
    #test one rate
    status_ = MPI.Status()
    while(True):
        accept_connection = np.array([True],dtype='b')
        comm.Send([accept_connection, MPI.BOOL], dest=0, tag=0)
        size=np.empty(1,dtype='i')
        comm.Recv([size, MPI.INT], source=0, tag=0)
        sys.stdout.flush()
        data = np.empty(size, dtype='d')
        comm.Recv([data,size, MPI.DOUBLE],source=0,tag=MPI.ANY_TAG,status=status_)
        if status_.Get_tag() == 0:
            print(data)
            print(np.sum(data))
            sys.stdout.flush()
        else:
            break

    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('exit');
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        analyse(sys.argv[1],sys.argv[2])
    else:
        print('missing argument')

