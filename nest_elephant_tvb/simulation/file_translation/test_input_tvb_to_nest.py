import numpy as np
import os
import numpy.random as rgn
from mpi4py import MPI

def input(path,nb_spike_detector):
    #Start communication channels
    path_to_files = path + nb_spike_detector + ".txt"
    min_delay = 200.0
    #For NEST
    # Init connection
    print("Waiting for port details")
    fport = open(path_to_files, "r")
    port = fport.readline()
    fport.close()
    print('wait connection '+port)
    sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('connect to '+port)
    #test one rate

    status_ = MPI.Status()
    current_step = np.empty(1, dtype='d')
    starting = 0.0
    while True:
        print("wait for send data")
        comm.Recv([current_step, 1, MPI.DOUBLE], source=0, tag=MPI.ANY_TAG, status=status_)
        if status_.Get_tag() == 0:
            if current_step[0] < starting:
                data = np.array([0],dtype='d')
                comm.Send([data, MPI.DOUBLE], dest=0, tag=1)
                sys.stdout.flush()
            else:
                size= np.random.randint(0,1000)
                time = starting+np.random.rand(size)*(min_delay-0.2)
                time = np.around(np.sort(np.array(time)),decimals=1)
                id = np.random.randint(0,10,size)
                data = np.ascontiguousarray(np.swapaxes([id,time],0,1),dtype='d')
                for i in data:
                    comm.Send([i, MPI.DOUBLE], dest=0, tag=0)
                    print(" send data ",i)
                comm.Send([i, MPI.DOUBLE], dest=0, tag=1)
                print(" ending", i)
                sys.stdout.flush();
                starting+=min_delay;
                if starting > 10000:
                    break
    print("ending" )
    comm.Send([current_step, MPI.DOUBLE], dest=0, tag=2)
    comm.Disconnect()
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

