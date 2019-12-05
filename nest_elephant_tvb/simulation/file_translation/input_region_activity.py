import numpy as np
import os
import numpy.random as rgn
from mpi4py import MPI

def input(path,nb_spike_detector):
    #Start communication channels
    # path_to_files = "/home/kusch/Documents/project/co_simulation/cosim_TVB_NEST/nest-io/pynest/examples/"
    # path_to_files = "/home/kusch/Documents/project/co_simulation/cosim_TVB_NEST/translator/test/config_mpi/" + nb_spike_detector + ".txt"
    path_to_files = path + nb_spike_detector + ".txt"
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
            if status_.Get_tag() == 0 :
                data = starting+np.random.rand(20)*100
                data = np.around(np.sort(np.array(data,dtype='d')),decimals=1)
                for i in data:
                    comm.Send([i, MPI.DOUBLE], dest=0, tag=0)
                    print(" send data ",i)
                comm.Send([i, MPI.DOUBLE], dest=0, tag=1)
                print(" ending", i)
                sys.stdout.flush();
                starting+=100;
            else:
                comm.Disconnect()
                comm = MPI.COMM_WORLD.Accept(port, info, root)

    comm.Disconnect()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('exit');
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        input(sys.argv[1],sys.argv[2])
    else:
        print('missing argument')

