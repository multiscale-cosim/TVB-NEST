#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import os
import json
from nest_elephant_tvb.translation.mpi.Nest_IO import Send_Data_to_Nest
from nest_elephant_tvb.translation.mpi.TVB_IO import Receive_TVB_Data
from nest_elephant_tvb.translation.mpi.translation_function import Translation_rate_to_spike


if __name__ == "__main__":
    import sys

    if len(sys.argv)!=5:
        print('missing argument')
        exit (1)

    # Parse arguments
    path_config = sys.argv[1]
    path = path_config+'/../../'
    id_first_spike_detector = int(sys.argv[2])
    nb_spike_generator = int(sys.argv[3])
    TVB_config = sys.argv[4]


    # object for analysing data
    with open(path_config+'/../../parameter.json') as f:
        parameters = json.load(f)
    param = parameters['param_TR_tvb_to_nest']
    level_log = param['level_log']

    if MPI.COMM_WORLD.Get_size() == 3:
        rank = MPI.COMM_WORLD.Get_rank()
        if rank == 0:
            send_data_to_Nest = Send_Data_to_Nest(id_first_spike_detector,2,'tvb_to_nest_sender' + str(id_first_spike_detector), path,level_log,0,buffer_r_w=[0,2])
            path_to_files_sends = []
            for i in range(nb_spike_generator):
                # write file with port and unlock
                path_to_files_send = os.path.join(path_config, str(id_first_spike_detector+i) + ".txt")
                path_to_files_sends.append(path_to_files_send)
            send_data_to_Nest.run(path_to_files_sends)
        elif rank == 1:
            #  Create the port, file and set unlock for receiver
            receive_data_to_TVB = Receive_TVB_Data(2,'tvb_to_nest_receiver'+str(id_first_spike_detector),path,level_log,1,buffer_r_w=[0,2])
            path_to_files_receive = [path_config + TVB_config]
            receive_data_to_TVB.run(path_to_files_receive)
        elif rank == 2:
            translate_rate_to_spike = Translation_rate_to_spike(param,1,nb_spike_generator, 'tvb_to_nest_translate' + str(id_first_spike_detector), path, level_log, 2,buffer_r_w=[0,2])
            translate_rate_to_spike.run(None)
        else :
            raise Exception('too much rank')
    elif MPI.COMM_WORLD.Get_size() == 1:
        pass
    else:
        raise Exception(' BAD number of MPI rank')