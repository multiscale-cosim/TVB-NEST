#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import os
import json
from nest_elephant_tvb.translation.simulator_IO.Nest_IO import Send_Data_to_Nest
from nest_elephant_tvb.translation.simulator_IO.TVB_IO import Receive_TVB_Data
from nest_elephant_tvb.translation.simulator_IO.translation_function import Translation_rate_to_spike
from nest_elephant_tvb.translation.communication.internal_mpi import MPI_communication
from nest_elephant_tvb.translation.communication.internal_thread import Thread_communication

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
            send_data_to_Nest = Send_Data_to_Nest(id_first_spike_detector,'tvb_to_nest_sender' + str(id_first_spike_detector), path,level_log,
                                                  communication_intern=MPI_communication,buffer_r_w=[0,2])
            path_to_files_sends = []
            for i in range(nb_spike_generator):
                # write file with port and unlock
                path_to_files_send = os.path.join(path_config, str(id_first_spike_detector+i) + ".txt")
                path_to_files_sends.append(path_to_files_send)
            send_data_to_Nest.run(path_to_files_sends)
        elif rank == 1:
            #  Create the port, file and set unlock for receiver
            receive_data_to_TVB = Receive_TVB_Data('tvb_to_nest_receiver'+str(id_first_spike_detector),path,level_log,
                                                   communication_intern=MPI_communication,receiver_rank=2,buffer_r_w=[0,2])
            path_to_files_receive = [path_config + TVB_config]
            receive_data_to_TVB.run(path_to_files_receive)
        elif rank == 2:
            translate_rate_to_spike = Translation_rate_to_spike(param,nb_spike_generator, 'tvb_to_nest_translate' + str(id_first_spike_detector), path, level_log,
                                                                communication_intern=MPI_communication,sender_rank=1,buffer_r_w=[0,2])
            translate_rate_to_spike.run(None)
        else :
            raise Exception('too much rank')
    elif MPI.COMM_WORLD.Get_size() == 1:
        from threading import Thread
        import numpy as np
        receive_data_to_TVB = Receive_TVB_Data('tvb_to_nest_receiver'+str(id_first_spike_detector),path,level_log,
                                                    communication_intern=Thread_communication,
                                                    buffer_write_status=np.ones(1),
                                                    buffer_write_shape=(2,2),
                                               )
        path_to_files_receive = [path_config + TVB_config]
        translate_rate_to_spike = Translation_rate_to_spike(param,nb_spike_generator, 'tvb_to_nest_translate' + str(id_first_spike_detector), path, level_log,
                                                                communication_intern=Thread_communication,
                                                            buffer_write_status=np.ones((1, 1), dtype=np.int)*-2,
                                                            buffer_write_shape=(1000000 * 3, 1),
                                                            buffer_read=receive_data_to_TVB.communication_internal.buffer_write_data,
                                                            status_read=receive_data_to_TVB.communication_internal.status_write,
                                                            lock_read=  receive_data_to_TVB.communication_internal.lock_write
                                                            )
        send_data_to_Nest = Send_Data_to_Nest(id_first_spike_detector,
                                              'tvb_to_nest_sender' + str(id_first_spike_detector), path,level_log,
                                              communication_intern=Thread_communication,
                                              buffer_read=translate_rate_to_spike.communication_internal.buffer_write_data,
                                              status_read=translate_rate_to_spike.communication_internal.status_write,
                                              lock_read=  translate_rate_to_spike.communication_internal.lock_write
                                              )
        path_to_files_sends = []
        for i in range(nb_spike_generator):
            # write file with port and unlock
            path_to_files_send = os.path.join(path_config, str(id_first_spike_detector + i) + ".txt")
            path_to_files_sends.append(path_to_files_send)
        th_receive = Thread(target=receive_data_to_TVB.run, args=(path_to_files_receive,))
        th_translation = Thread(target=translate_rate_to_spike.run, args=(None,))
        th_send = Thread(target=send_data_to_Nest.run, args=(path_to_files_sends,))
        th_receive.start()
        th_translation.start()
        th_send.start()
        th_translation.join()
        th_receive.join()
        th_send.join()
    else:
        raise Exception(' BAD number of MPI rank')