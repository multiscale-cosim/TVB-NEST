#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
from mpi4py import MPI

import os
import time

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

    while not os.path.exists(path):
        print ("Port file not found yet, retry in 1 second")
        time.sleep(1)


    fport = open(path, "r")
    port = fport.readline()
    fport.close()
    print('Nest Output : wait connection '+ port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('Nest Output : connect to '+ port) ;sys.stdout.flush()

    starting = 0.1 # the begging of each time of synchronization
    check = np.empty(1,dtype='b')
    status_ = MPI.Status() # status of the different message
    while True:
        # wait until the translator accept the connections
        comm.Send([np.array([True],dtype='b'), 1, MPI.CXX_BOOL], dest=0, tag=0)
        comm.Recv([check, 1, MPI.CXX_BOOL], source=MPI.ANY_SOURCE, tag=0,status=status_)
        # create random data
        size= np.random.randint(0,1000)
        times = starting+np.random.rand(size)*(min_delay-0.1)
        times = np.around(np.sort(np.array(times)),decimals=1)
        id_neurons = np.random.randint(0,10,size)
        id_detector = np.random.randint(0,10,size)
        data = np.ascontiguousarray(np.swapaxes([id_detector,id_neurons,times],0,1),dtype='d')
        # send data one by one like spike generator
        comm.Send([np.array([size*3],dtype='i'),1, MPI.INT], dest=status_.Get_source(), tag=0)
        comm.Send([data,size*3, MPI.DOUBLE], dest=status_.Get_source(), tag=0)
        # ending the actual run
        comm.Send([np.array([True],dtype='b'), 1, MPI.CXX_BOOL], dest=0, tag=1)
        #print result and go to the next run
        print("Nest Output : ",comm.Get_rank(),size);sys.stdout.flush()
        starting+=min_delay
        if starting > 10000:
            break
    # closing the connection at this end
    print("Nest Output : ending" );sys.stdout.flush()
    # send the signal for end the translation
    comm.Send([np.array([True], dtype='b'), 1, MPI.CXX_BOOL], dest=0, tag=2)
    print("Nest Output : ending" );sys.stdout.flush()
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

