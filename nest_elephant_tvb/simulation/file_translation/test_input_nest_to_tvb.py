import numpy as np
from mpi4py import MPI

def simulate_spike_detector(path,min_delay):
    '''
    simulate spike dectector output for testing the nest to tvb translator input
    :param path: the path to the file for the connections
    :param min_delay: the time of one simulation
    :return:
    '''
    # Init connection from file connection
    print(path)
    print("Waiting for port details");sys.stdout.flush()
    fport = open(path, "r")
    port = fport.readline()
    fport.close()
    print('wait connection '+ port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('connect to '+ port) ;sys.stdout.flush()

    current_step = np.empty(1, dtype='d')
    starting = 0.0
    while True:
        # wait until the translatro acept the connections
        accept = False
        while not accept:
            req = comm.irecv(source=0,tag=0)
            accept = req.wait()
        # create random data
        size= np.random.randint(0,1000)
        time = starting+np.random.rand(size)*(min_delay-0.2)
        time = np.around(np.sort(np.array(time)),decimals=1)
        id = np.random.randint(0,10,size)
        data = np.ascontiguousarray(np.swapaxes([id,time],0,1),dtype='d')
        # send data one by one like spike generator
        for i in data:
            comm.Send([i, MPI.DOUBLE], dest=0, tag=0)
            # print(" send data ",i)
        # ending the actual run
        comm.Send([i, MPI.DOUBLE], dest=0, tag=1)
        #print result and go to the next run
        print(comm.Get_rank(),size);sys.stdout.flush()
        starting+=min_delay
        if starting > 10000:
            break
    # closing the connection at this end
    print("ending" );sys.stdout.flush()
    # send the signal for end the translation
    comm.Send([current_step, MPI.DOUBLE], dest=0, tag=2)
    comm.Disconnect()
    MPI.Close_port(port)
    MPI.Finalize()
    print('exit');sys.stdout.flush()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        simulate_spike_detector(sys.argv[1],float(sys.argv[2]))
    else:
        print('missing argument')

