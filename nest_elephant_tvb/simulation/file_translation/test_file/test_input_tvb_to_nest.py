import numpy as np
from mpi4py import MPI

def simulate_TVB_output(path,min_delay):
    '''
    simulate the input of the translator tvb_to_nest
    :param path: the path to the file for the connections
    :param nb_spike_detector:
    :return:
    '''
    # Init connection from file connection
    print("Waiting for port details");sys.stdout.flush()
    fport = open(path, "r")
    port = fport.readline()
    fport.close()
    print('wait connection '+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('connect to '+port);sys.stdout.flush()

    status_ = MPI.Status()
    starting = 0.0 # the begging of each time of synchronization
    while True:
        # wait until the translator accept the connections
        accept = False
        while not accept:
            req = comm.irecv(source=0,tag=0)
            accept = req.wait(status_)
        source = status_.Get_source() # the id of the excepted source
        # create random data
        size= int(min_delay/0.1 )
        rate = np.random.rand(size)*400
        data = np.ascontiguousarray(rate,dtype='d') # format the rate for sending
        shape = np.array(data.shape[0],dtype='i') # size of data
        times = np.array([starting,starting+min_delay],dtype='d') # time of stating and ending step
        comm.Send([times,MPI.DOUBLE],dest=source,tag=0)
        comm.Send([shape,MPI.INT],dest=source,tag=0)
        comm.Send([data, MPI.DOUBLE], dest=source, tag=0)
        # print result and go to the next run
        print(data,times,shape);sys.stdout.flush() # printing summary of the data
        starting+=min_delay
        if starting > 10000:
            break
    print("ending" );sys.stdout.flush()
    comm.Send([times, MPI.DOUBLE], dest=0, tag=2)
    comm.Disconnect()
    MPI.Close_port(port)
    print('exit');
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        simulate_TVB_output(sys.argv[1],float(sys.argv[2]))
    else:
        print('missing argument')

