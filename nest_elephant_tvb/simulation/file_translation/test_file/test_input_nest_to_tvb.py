import numpy as np
from mpi4py import MPI

def simulate_spike_detector(path,min_delay):
    '''
    simulate spike detector output for testing the nest to tvb translator input
    :param path: the path to the file for the connections
    :param min_delay: the time of one simulation
    :return:
    '''
    # Init connection from file connection
    print(path)
    print("Nest Output : Waiting for port details");sys.stdout.flush()
    fport = open(path, "r")
    port = fport.readline()
    fport.close()
    print('Nest Output : wait connection '+ port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('Nest Output : connect to '+ port) ;sys.stdout.flush()

    starting = 0.0 # the begging of each time of synchronization
    while True:
        # wait until the translator accept the connections
        accept = np.array([False],dtype='b')
        while not accept[0]:
            req = comm.Irecv([accept,1,MPI.BOOL],source=0,tag=0)
            req.wait()
        # create random data
        size= np.random.randint(0,1000)
        time = starting+np.random.rand(size)*(min_delay-0.2)
        time = np.around(np.sort(np.array(time)),decimals=1)
        id = np.random.randint(0,10,size)
        data = np.ascontiguousarray(np.swapaxes([id,time],0,1),dtype='d')
        # send data one by one like spike generator
        for i in data:
            comm.Send([i, MPI.DOUBLE], dest=0, tag=0)
            # print("Nest Output :  send data ",i)
        # ending the actual run
        comm.Send([i, MPI.DOUBLE], dest=0, tag=1)
        #print result and go to the next run
        print("Nest Output : ",comm.Get_rank(),size);sys.stdout.flush()
        starting+=min_delay
        if starting > 10000:
            break
    # closing the connection at this end
    print("Nest Output : ending" );sys.stdout.flush()
    # send the signal for end the translation
    comm.Send([i, MPI.DOUBLE], dest=0, tag=2)
    comm.Disconnect()
    MPI.Close_port(port)
    MPI.Finalize()
    print('Nest Output : exit');sys.stdout.flush()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        simulate_spike_detector(sys.argv[1],float(sys.argv[2]))
    else:
        print('missing argument')

