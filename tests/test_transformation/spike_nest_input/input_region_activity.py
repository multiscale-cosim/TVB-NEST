#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
import os
import numpy.random as rgn
from mpi4py import MPI


def input(path):
    """
    Simulate some random spike train input
    :param path: the file for the configurations of the connection
    :return:
    """
    # Start communication channels
    path_to_files = path
    # For NEST
    # Init connection
    print("INPUT : Waiting for port details")
    info = MPI.INFO_NULL
    root = 0
    port = MPI.Open_port(info)
    fport = open(path_to_files, "w+")
    fport.write(port)
    fport.close()
    print('INPUT : wait connection ' + port); sys.stdout.flush()
    comm = MPI.COMM_WORLD.Accept(port, info, root)
    print('INPUT : connect to ' + port)

    # test one rate
    status_ = MPI.Status()
    check = np.empty(1, dtype='b')
    starting = 1
    while True:
        comm.Recv([check, 1, MPI.CXX_BOOL], source=0, tag=MPI.ANY_TAG, status=status_)
        print("INPUT :  start to send"); sys.stdout.flush()
        print("INPUT :  status a tag ", status_.Get_tag()); sys.stdout.flush()
        if status_.Get_tag() == 0:
            source = status_.Get_source()
            print("Input : source is", source); sys.stdout.flush()
            # receive list ids
            size_list = np.empty(1, dtype='i')
            comm.Recv([size_list, 1, MPI.INT], source=source, tag=0, status=status_)
            print("INPUT : size list id", size_list); sys.stdout.flush()
            if size_list[0] != 0:
                list_id = np.empty(size_list, dtype='i')
                comm.Recv([list_id, size_list, MPI.INT], source=source, tag=0, status=status_)
                print("INPUT :  id ", list_id); sys.stdout.flush()
                shape = np.random.randint(0, 100, 1, dtype='i')
                data = starting + np.random.rand(shape[0]) * 200
                data = np.around(np.sort(np.array(data, dtype='d')), decimals=1)
                send_shape = np.array(np.concatenate([shape, shape]), dtype='i')
                comm.Send([send_shape, MPI.INT], dest=source, tag=list_id[0])
                print("INPUT :  shape data ", shape); sys.stdout.flush()
                comm.Send([data, MPI.DOUBLE], dest=source, tag=list_id[0])
                print("INPUT :  send data", data); sys.stdout.flush()
                comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=status_)
            print("INPUT : end run"); sys.stdout.flush()
            starting += 200
        elif (status_.Get_tag() == 2):
            print("INPUT : end simulation")
            print("INPUT : ending time : ", starting); sys.stdout.flush()
            break
        else:
            print(status_.Get_tag())
            break
    comm.Barrier()
    comm.Disconnect()
    MPI.Close_port(port)
    os.remove(path_to_files)
    print('INPUT : exit')
    MPI.Finalize()


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        input(sys.argv[1])
    else:
        print('missing argument')
