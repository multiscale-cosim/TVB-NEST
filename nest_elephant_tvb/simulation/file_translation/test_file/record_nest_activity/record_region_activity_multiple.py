import numpy as np
import os
from mpi4py import MPI
import time

def analyse(path,nb_mpi):
    #Start communication channels
    path_to_files = path
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
    check = np.empty(1,dtype='b')
    source_sending = np.arange(0,comm.Get_remote_size(),1) # list of all the process for the commmunication
    while(True):
        comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        print(" start to send"); sys.stdout.flush()
        print(" status a tag ",status_.Get_tag()," source ", status_.Get_source()); sys.stdout.flush()
        if status_.Get_tag() == 0:
            for i in range(nb_mpi-1):
                comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=0, status=status_)
            for source in source_sending:
                print("source is", source); sys.stdout.flush()
                comm.Send([np.array(True,dtype='b'),MPI.BOOL],dest=source,tag=0)
                shape = np.empty(1, dtype='i')
                comm.Recv([shape, 1, MPI.INT], source=source, tag=0, status=status_)
                print("shape is", shape[0]); sys.stdout.flush()
                data = np.empty(shape[0], dtype='d')
                comm.Recv([data, shape[0], MPI.DOUBLE], source=status_.Get_source(), tag=0, status=status_)
                print("data is ", data); sys.stdout.flush()
        elif status_.Get_tag() == 1:
            print("end run");sys.stdout.flush()
        elif status_.Get_tag() ==2:
            for i in range(nb_mpi-1):
                print(" receive ending");sys.stdout.flush()
                comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
            print("end simulation");sys.stdout.flush()
            break
        else:
            print(status_.Get_tag())
            break
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('exit');
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)== 3 :
        analyse(sys.argv[1],int(sys.argv[2]))
    else:
        print('missing argument')

