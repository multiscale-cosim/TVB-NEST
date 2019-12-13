import numpy as np
from mpi4py import MPI

def simulate_TVB_reception(path):
    '''
    simulate the output of the translator for nest to TVB
    :param path: the path to the file for the connections
    :return:
    '''
    # Init connection from file connection
    print(path)
    print("Waiting for port details");sys.stdout.flush()
    fport = open(path, "r")
    port=fport.readline()
    fport.close()
    print("wait connection "+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('connect to '+port);sys.stdout.flush()

    status_ = MPI.Status()
    while(True):
        # send to the translator, I want the next part
        comm.Send([np.array([True],dtype='b'), MPI.BOOL], dest=0, tag=0)
        # get the size of the rate
        size=np.empty(1,dtype='i')
        comm.Recv([size, MPI.INT], source=0, tag=0)
        # get the rate
        rates = np.empty(size, dtype='d')
        comm.Recv([rates,size, MPI.DOUBLE],source=0,tag=MPI.ANY_TAG,status=status_)
        # print the summary of the data
        if status_.Get_tag() == 0:
            print(comm.Get_rank(),np.sum(rates), rates);sys.stdout.flush()
        else:
            break
    # closing the connection at this end
    comm.Disconnect()
    MPI.Close_port(port)
    print('exit');
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==2:
        simulate_TVB_reception(sys.argv[1])
    else:
        print('missing argument')

