#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import os
import json
from nest_elephant_tvb.translation.simulator_IO.Nest_IO import Receiver_Nest_Data
from nest_elephant_tvb.translation.simulator_IO.TVB_IO import Send_TVB_Data
from nest_elephant_tvb.translation.simulator_IO.translation_function import Translation_spike_to_rate
from nest_elephant_tvb.translation.communication.internal_mpi import MPI_communication
from nest_elephant_tvb.translation.communication.internal_thread import Thread_communication


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


    if MPI.COMM_WORLD.Get_size() == 3:
        rank = MPI.COMM_WORLD.Get_rank()
        if rank == 0:
            receive_data_from_nest = Receiver_Nest_Data('nest_to_tvb_receive' + str(id_spike_detector),
                                                        path,level_log,
                                                        communication_intern=MPI_communication,buffer_r_w=[2,0])
            path_to_files_receive = [path + file_spike_detector] # TODO: use proper path operations
            receive_data_from_nest.run(path_to_files_receive)
        elif rank == 1:
            send_data_to_TVB = Send_TVB_Data('nest_to_tvb_send'+str(id_spike_detector),path,level_log,
                                             communication_intern=MPI_communication,sender_rank=2,buffer_r_w=[2,0])
            path_to_files_send = [path + TVB_recev_file]
            send_data_to_TVB.run(path_to_files_send)
        elif rank == 2:
            translation = Translation_spike_to_rate(param,'nest_to_tvb_translate' + str(id_spike_detector), path, level_log,
                                             communication_intern=MPI_communication,receiver_rank=1,buffer_r_w=[2,0])
            translation.run(None)
        else :
            raise Exception('too much rank')
    elif MPI.COMM_WORLD.Get_size() == 1:
        from threading import Thread
        import numpy as np
        receive_data_from_nest = Receiver_Nest_Data('nest_to_tvb_receive' + str(id_spike_detector),
                                                    path,level_log,
                                                    communication_intern=Thread_communication,
                                                    buffer_write_status=np.ones((1,1),dtype=np.int)*-2,
                                                    buffer_write_shape=(1000000 * 3,1),
                                                    )
        path_to_files_receive = [path + file_spike_detector] # TODO: use proper path operations
        translation = Translation_spike_to_rate(param,'nest_to_tvb_translate' + str(id_spike_detector), path, level_log,
                                             communication_intern=Thread_communication,
                                             buffer_write_status=np.ones(1)*-2,
                                             buffer_write_shape=(2,int(param['synch']/param['resolution'])),
                                             buffer_read=receive_data_from_nest.communication_internal.buffer_write_data,
                                             status_read=receive_data_from_nest.communication_internal.status_write,
                                             lock_read=receive_data_from_nest.communication_internal.lock_write
                                                )
        send_data_to_TVB = Send_TVB_Data('nest_to_tvb_send'+str(id_spike_detector),path,level_log,
                                             communication_intern=Thread_communication,
                                             buffer_read=translation.communication_internal.buffer_write_data,
                                             status_read=translation.communication_internal.status_write,
                                             lock_read=translation.communication_internal.lock_write
                                         )
        path_to_files_send = [path + TVB_recev_file]

        th_receive = Thread(target=receive_data_from_nest.run, args=(path_to_files_receive,))
        th_translation = Thread(target=translation.run, args=(None,))
        th_send = Thread(target=send_data_to_TVB.run, args=(path_to_files_send,))
        th_receive.start()
        th_translation.start()
        th_send.start()
        th_translation.join()
        th_receive.join()
        th_send.join()
    else:
        raise Exception('BAD number of MPI rank')