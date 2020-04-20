import numpy as np
import os
import numpy.random as rgn
from mpi4py import MPI

def input(path,nb_mpi):
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
    sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('connect to '+port)
    #test one rate

    status_ = MPI.Status()
    check = np.empty(1,dtype='b')
    starting = 1
    count=0
    count_send=0
    while True:
        comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
        print(" start to send"); sys.stdout.flush()
        print(" status a tag ",status_.Get_tag() ); sys.stdout.flush()
        if status_.Get_tag() == 0 :
            id = np.empty(1, dtype='i')
            print(" receive id ");sys.stdout.flush()
            print(" source "+str(status_.Get_source()));sys.stdout.flush()
            comm.Recv([id, 1, MPI.INT], source=status_.Get_source(), tag=0)
            print(" id ", id);sys.stdout.flush()
            count += 1
            if count_send % nb_mpi == 0:
                shape = np.random.randint(0,50,1,dtype='i')*2
                data = starting+np.random.rand(shape[0])*200
                data = np.around(np.sort(np.array(data,dtype='d')),decimals=1)
            comm.Send([shape, MPI.INT], dest=status_.Get_source(), tag=id[0])
            print(" shape data ",shape);sys.stdout.flush()
            comm.Send([data, MPI.DOUBLE], dest=status_.Get_source(), tag=id[0])
            print(" send data", data);sys.stdout.flush()
        elif status_.Get_tag() == 1:
            print("end run");sys.stdout.flush()
            count += 1
            if count % nb_mpi ==  0:
                starting+=200
        elif (status_.Get_tag() == 2):
            for i in range(nb_mpi-1):
                print(" receive ending");sys.stdout.flush()
                comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status_)
            print(" receive ending"); sys.stdout.flush()
            print("end simulation"); sys.stdout.flush()
            print("ending time : ",starting)
            break
        else:
            print(status_.Get_tag())
            break
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('exit')
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        input(sys.argv[1],int(sys.argv[2]))
    else:
        print('missing argument')

