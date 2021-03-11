#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
from mpi4py import MPI
import os
import time


def simulate_TVB_reception(path):
    '''
    simulate the receptor of the translator for nest to TVB
    :param path: the path to the file for the connections
    :return:
    '''
    # Init connection from file connection
    print(path)
    print("TVB INPUT : Waiting for port details");sys.stdout.flush()

    while not os.path.exists(path):
        print ("Port file not found yet, retry in 1 second")
        time.sleep(1)

    fport = open(path, "r")
    port=fport.readline()
    fport.close()
    print("TVB INPUT :wait connection "+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('TVB INPUT :connect to '+port);sys.stdout.flush()

    status_ = MPI.Status()
    while(True):
        # send to the translator, I want the next part
        req = comm.isend(True, dest=0, tag=0)
        req.wait()

        times=np.empty(2,dtype='d')
        comm.Recv([times, MPI.FLOAT], source=0, tag=0)
        # get the size of the rate
        size=np.empty(1,dtype='i')
        comm.Recv([size, MPI.INT], source=0, tag=0)
        # get the rate
        rates = np.empty(size, dtype='d')
        comm.Recv([rates,size, MPI.DOUBLE],source=0,tag=MPI.ANY_TAG,status=status_)
        # print the summary of the data
        if status_.Get_tag() == 0:
            print("TVB INPUT :",comm.Get_rank(),times,np.sum(rates));sys.stdout.flush()
        else:
            break
        if times[1] >9900:
            break
    # closing the connection at this end
    req = comm.isend(True, dest=0, tag=1)
    req.wait()
    print('TVB INPUT :end');sys.stdout.flush()
    comm.Disconnect()
    MPI.Close_port(port)
    print('TVB INPUT :exit');sys.stdout.flush()
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==2:
        simulate_TVB_reception(sys.argv[1])
    else:
        print('missing argument')

