#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
from mpi4py import MPI
import os
import time
import sys

def simulate_TVB_output(path,min_delay):
    '''
    simulate the input of the translator tvb_to_nest
    :param path: the path to the file for the connections
    :param min_delay: the time of one simulation
    :return:
    '''
    max_mpi_connection_attempts = 50
    file_unlock=False
    for attempt in range(max_mpi_connection_attempts):
        if os.path.exists(path+".unlock"):
            print ("MPI connection file available after t={0} seconds".format(attempt));sys.stdout.flush()
            file_unlock=True
            break

        time.sleep(1)


    if file_unlock is False:
        print("Could file not unlocked after 20 attempts, exit");sys.stdout.flush()
        sys.exit (1)


    # Init connection from file connection
    print("TVB_OUTPUT : Waiting for port details");sys.stdout.flush()
    fport = open(path, "r")
    port = fport.readline()
    fport.close()
    print('TVB_OUTPUT :wait connection: '+ port + ": " + path );sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('TVB_OUTPUT :connect to '+port);sys.stdout.flush()
       
    print('TVB_OUTPUT: Done with connection loop, EXIT after 1 second');sys.stdout.flush() 

    time.sleep(1)
    return

    status_ = MPI.Status()
    starting = 0.0 # the begging of each time of synchronization
    while True:
        # wait until the translator accept the connections
        accept = False
        print("TVB_OUTPUT :wait acceptation");sys.stdout.flush()
        while not accept:
            req = comm.irecv(source=0,tag=0)
            accept = req.wait(status_)
        print("TVB_OUTPUT :acceptated");sys.stdout.flush()
        source = status_.Get_source() # the id of the excepted source
        # create random data
        size= int(min_delay/0.1 )
        rate = np.random.rand(size)*400
        data = np.ascontiguousarray(rate,dtype='d') # format the rate for sending
        shape = np.array(data.shape[0],dtype='i') # size of data
        times = np.array([starting,starting+min_delay],dtype='d') # time of stating and ending step
        print("TVB_OUTPUT :send time : " +str(times));sys.stdout.flush()
        comm.Send([times,MPI.DOUBLE],dest=source,tag=0)
        print("TVB_OUTPUT :send shape : " +str(shape));sys.stdout.flush()
        comm.Send([shape,MPI.INT],dest=source,tag=0)
        print("TVB_OUTPUT :send data : " +str(np.sum(np.sum(data))));sys.stdout.flush()
        comm.Send([data, MPI.DOUBLE], dest=source, tag=0)
        # print result and go to the next run
        starting+=min_delay
        if starting > 10000:
            break
    print("TVB_OUTPUT :ending" );sys.stdout.flush()
    accept = False
    print("TVB_OUTPUT :wait acceptation");sys.stdout.flush()
    while not accept:
         req = comm.irecv(source=0,tag=0)
         accept = req.wait(status_)
    print("TVB_OUTPUT :ending" );sys.stdout.flush()
    comm.Send([times, MPI.DOUBLE], dest=0, tag=1)
    comm.Disconnect()
    MPI.Close_port(port)
    print('TVB_OUTPUT :exit')
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        simulate_TVB_output(sys.argv[1],float(sys.argv[2]))
    else:
        print('missing argument')

