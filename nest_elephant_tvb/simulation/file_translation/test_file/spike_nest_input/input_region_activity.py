import numpy as np
import os
import numpy.random as rgn
from mpi4py import MPI

def input(path):
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
    ids = np.empty(2, dtype='i')
    thread_id = np.empty(1, dtype='i')
    starting = 1
    while True:
        comm.Recv([ids, 2, MPI.INT], source=0, tag=MPI.ANY_TAG, status=status_)
        if status_.Get_tag() == 0 :
            shape = np.random.randint(0,100,1,dtype='i')
            data = starting+np.random.rand(shape[0])*200
            data = np.around(np.sort(np.array(data,dtype='d')),decimals=1)
            comm.Send([shape, MPI.INT], dest=status_.Get_source(), tag=ids[1])
            print(" shape data ",shape);sys.stdout.flush()
            comm.Send([data, MPI.DOUBLE], dest=status_.Get_source(), tag=ids[1])
            print(" send data", data);sys.stdout.flush()
            comm.Recv([thread_id, 1, MPI.INT], source=status_.Get_source(), tag=MPI.ANY_TAG, status=status_)
            print("end run");sys.stdout.flush()
            starting+=200
        elif(status_.Get_tag() ==2):
            print("end simulation");sys.stdout.flush()
            print(starting)
            comm.Disconnect()
            comm = MPI.COMM_WORLD.Accept(port, info, root)
            if starting > 1000:
                starting = 1
        else:
            print(status_.Get_tag())
            break
    comm.Disconnect()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('exit');
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==2:
        input(sys.argv[1])
    else:
        print('missing argument')

