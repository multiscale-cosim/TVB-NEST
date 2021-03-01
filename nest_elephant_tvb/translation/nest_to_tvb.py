#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import os
import json
from nest_elephant_tvb.translation.Nest_IO import Receiver_Nest_Data
from nest_elephant_tvb.translation.TVB_IO import Send_TVB_Data
from nest_elephant_tvb.translation.translation_function import Translation_spike_to_rate


if __name__ == "__main__":
    import sys

    if len(sys.argv)!=4:
        print('incorrect number of arguments')
        exit(1)
    
    path = sys.argv[1]
    file_spike_detector = sys.argv[2]
    TVB_recev_file = sys.argv[3]
    
    # take the parameters and instantiate objects for analysing data
    with open(path+'/parameter.json') as f:
        parameters = json.load(f)
    param = parameters['param_TR_nest_to_tvb']
    level_log = param['level_log']
    id_spike_detector = os.path.splitext(os.path.basename(path+file_spike_detector))[0]


    rank = MPI.COMM_WORLD.Get_rank()
    if rank == 0:
        receive_data_from_nest = Receiver_Nest_Data('nest_to_tvb_receive' + str(id_spike_detector),
                                                    path,level_log,0,buffer_r_w=[2,0])
        path_to_files_receive = [path + file_spike_detector] # TODO: use proper path operations
        receive_data_from_nest.run(path_to_files_receive)
    elif rank == 1:
        send_data_to_TVB = Send_TVB_Data(2,'nest_to_tvb_send'+str(id_spike_detector),path,level_log,1,buffer_r_w=[2,0])
        path_to_files_send = [path + TVB_recev_file]
        send_data_to_TVB.run(path_to_files_send)
    elif rank == 2:
        send_data_to_TVB = Translation_spike_to_rate(param,1, 'nest_to_tvb_translate' + str(id_spike_detector), path, level_log, 2,
                                         buffer_r_w=[2,0])
        send_data_to_TVB.run(None)
    else :
        raise Exception('too much rank')
