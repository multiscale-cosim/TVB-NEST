#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
from mpi4py import MPI
import os
import time

def simulate_nest_generator(path,file,nb_generator):
    '''
    simulate the spike generator of the transform for tvb to nest
    :param path: the path to the file for the connections
    :return:
    '''
    # Init connection

    np.savetxt(path+'//nest/spike_generator.txt',np.array([i for i in range(nb_generator)],dtype=int),fmt='%i')
    np.savetxt(path+'//nest/spike_generator.txt.unlock',np.array([0],dtype=int),fmt='%i')

    max_mpi_connection_attempts = 600 # wait 1min
    file_unlock=False
    for attempt in range(max_mpi_connection_attempts):
        # print("file to read",path+file);sys.stdout.flush()
        if os.path.exists(path+file+".unlock"):
            print("file to read",path+file);sys.stdout.flush()
            print("MPI connection file available after t={0} seconds".format(attempt));sys.stdout.flush()
            file_unlock=True
            break
        else:
            time.sleep(0.1)

    if file_unlock is False:
        print("Could file not unlocked after 20 attempts, exit");sys.stdout.flush()
        sys.exit (1)

    print("Nest_Input:" + path+file)
    print("Nest_Input :Waiting for port details");sys.stdout.flush()
    fport = open(path+file, "r")
    port=fport.readline()
    fport.close()
    print("Nest_Input :wait connection "+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('Nest_Input :connect to '+port);sys.stdout.flush()

    status_ = MPI.Status()
    ids=np.arange(0,10,1) # random id of spike detector
    print(ids);sys.stdout.flush()
    while(True):
        # Send start simulation
        comm.Send([np.array([True], dtype='b'), MPI.CXX_BOOL], dest=0, tag=0)
        comm.Send([np.array(10,dtype='i'), MPI.INT], dest=0, tag=0)
        # send ID of spike generator
        comm.Send([np.array(ids,dtype='i'), MPI.INT], dest=0, tag=0)
        # receive the number of spikes for updating the spike detector
        size=np.empty(11,dtype='i')
        comm.Recv([size,11, MPI.INT], source=0, tag=ids[0],status=status_)
        print("Nest_Input (" + str(ids[0]) + ") :receive size : " + str(size));sys.stdout.flush()
        # receive the spikes for updating the spike detector
        data = np.empty(size[0], dtype='d')
        comm.Recv([data,size[0], MPI.DOUBLE],source=0,tag=ids[0],status=status_)
        print("Nest_Input (" + str(id) + ") : " + str(np.sum(data)));sys.stdout.flush()
        # printing value and exist
        print("Nest_Input: Before print ");sys.stdout.flush()
        if ids[0] == 0:
            print ("Nest_Input:" + str([ids[0], data,np.sum(data)]) );sys.stdout.flush()
        print ("Nest_Input: debug end of loop");sys.stdout.flush()
        #send ending the the run of the simulation
        print("Nest_Input: Debug before send");sys.stdout.flush()
        comm.Send([np.array([True], dtype='b'), MPI.CXX_BOOL], dest=0, tag=1)
        print("Nest_Input: Debug after  send");sys.stdout.flush()

        print ("Nest_Input: before break");sys.stdout.flush()
        # print ("Nest_Input: before break" + str(data > 10000));sys.stdout.flush()
        if np.any(data > 10000):
            break

    # closing the connection at this end
    print('Nest_Input : Disconnect')
    comm.Send([np.array([True], dtype='b'), MPI.CXX_BOOL], dest=0, tag=2)
    comm.Disconnect()
    MPI.Close_port(port)
    print('Nest_Input :exit')
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==4:
        simulate_nest_generator(sys.argv[1],sys.argv[2],int(sys.argv[3]))
    else:
        print('missing argument')

