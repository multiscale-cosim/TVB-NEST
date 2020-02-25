import numpy as np
from mpi4py import MPI

def simulate_nest_generator(path):
    '''
    simulate the spike generator of the translator for tvb to nest
    :param path: the path to the file for the connections
    :return:
    '''
    # Init connection
    print(path)
    print("Waiting for port details");sys.stdout.flush()
    fport = open(path, "r")
    port=fport.readline()
    fport.close()
    print("wait connection "+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('connect to '+port);sys.stdout.flush()

    status_ = MPI.Status()
    ids=np.arange(0,10,1) # random id of spike detector
    thread=0
    print(ids);sys.stdout.flush()
    while(True):
        for id in ids:
            message_ids = np.array([id,thread],dtype='i')
            # send ID of spike generator
            comm.Send([np.array(message_ids,dtype='i'), MPI.INT], dest=0, tag=0)
            # receive the number of spikes for updating the spike detector
            size=np.empty(1,dtype='i')
            comm.Recv([size,1, MPI.INT], source=0, tag=thread,status=status_)
            # receive the spikes for updating the spike detector
            data = np.empty(size, dtype='d')
            comm.Recv([data,size, MPI.DOUBLE],source=0,tag=thread,status=status_)
            # printing value and exist
            if status_.Get_tag() == thread:
                print(id, data,np.sum(data));sys.stdout.flush()
            else:
                break
        #send ending the the run of the simulation
        comm.Send([np.array(id,dtype='i'), MPI.INT], dest=0, tag=1)
    # closing the connection at this end
    comm.Disconnect()
    MPI.Close_port(port)
    print('exit');
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==2:
        simulate_nest_generator(sys.argv[1])
    else:
        print('missing argument')

