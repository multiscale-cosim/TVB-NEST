#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import os
import json
import time
import numpy as np
from nest_elephant_tvb.utils import create_logger
from nest_elephant_tvb.translation.simulator_IO.Nest_IO import Receiver_Nest_Data
from nest_elephant_tvb.translation.simulator_IO.TVB_IO import Send_TVB_Data
from nest_elephant_tvb.translation.simulator_IO.translation_function import Translation_spike_to_rate
from nest_elephant_tvb.translation.communication.internal_mpi import MPI_communication
from nest_elephant_tvb.translation.communication.internal_thread import Thread_communication


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print('incorrect number of arguments')
        exit(1)

    # Parse arguments
    path = sys.argv[1]  # path of the simulation
    id_translator = int(sys.argv[2])  # index of the translator

    # take the parameters and instantiate objects
    with open(path+'/parameter.json') as f:
        parameters = json.load(f)
    id_proxy = parameters['param_co_simulation']['id_region_nest']
    param = parameters['param_TR_nest_to_tvb']
    level_log = param['level_log']
    logger = create_logger(path,'nest_to_tvb_'+str(id_translator),level_log)
    rank = MPI.COMM_WORLD.Get_rank()

    while not os.path.exists(path + '/nest/spike_detector.txt.unlock'):
        logger.info("spike detector ids not found yet, retry in 1 second")
        time.sleep(1)
    spike_detector = np.loadtxt(path + '/nest/spike_detector.txt', dtype=int)
    # case of one spike detector
    try:
        spike_detector = np.array([int(spike_detector)])
    except:
        pass

    id_spike_detector = spike_detector[id_translator]
    file_spike_detector = "/translation/spike_detector/" + str(id_spike_detector) + ".txt"
    TVB_recev_file = "/translation/send_to_tvb/" + str(id_proxy[id_translator]) + ".txt"
    id_spike_detector = os.path.splitext(os.path.basename(path+file_spike_detector))[0]

    if MPI.COMM_WORLD.Get_size() == 3:  # MPI internal communication
        if rank == 0:  # communication with Nest
            receive_data_from_nest = Receiver_Nest_Data(
                'nest_to_tvb_receive' + str(id_spike_detector), path, level_log,
                communication_intern=MPI_communication, buffer_r_w=[2, 0])
            path_to_files_receive = [path + file_spike_detector]
            receive_data_from_nest.run(path_to_files_receive)
        elif rank == 1:  # communication with TVB
            send_data_to_TVB = Send_TVB_Data(
                'nest_to_tvb_send'+str(id_spike_detector), path, level_log,
                communication_intern=MPI_communication, sender_rank=2, buffer_r_w=[2, 0])
            path_to_files_send = [path + TVB_recev_file]
            send_data_to_TVB.run(path_to_files_send)
        elif rank == 2:  # translation from spike to rate
            translation = Translation_spike_to_rate(
                param,
                'nest_to_tvb_translate' + str(id_spike_detector), path, level_log,
                communication_intern=MPI_communication, receiver_rank=1, buffer_r_w=[2, 0])
            translation.run(None)
        else:
            raise Exception('too much rank')
    elif MPI.COMM_WORLD.Get_size() == 1:  # Thread internal communication
        from threading import Thread
        import numpy as np
        # creation of the object for Nest communication
        receive_data_from_nest = Receiver_Nest_Data(
            'nest_to_tvb_receive' + str(id_spike_detector), path, level_log,
            communication_intern=Thread_communication,
            buffer_write_status=np.ones((1, 1), dtype=np.int)*-2,
            buffer_write_shape=(1000000 * 3, 1),
            )
        path_to_files_receive = [path + file_spike_detector]
        # creation of the object for the translation from rate to spike
        translation = Translation_spike_to_rate(
            param,
            'nest_to_tvb_translate' + str(id_spike_detector), path, level_log,
            communication_intern=Thread_communication,
            buffer_write_status=np.ones(1)*-2,
            buffer_write_shape=(2, int(param['synch']/param['resolution'])),
            buffer_read=receive_data_from_nest.communication_internal.buffer_write_data,
            status_read=receive_data_from_nest.communication_internal.status_write,
            lock_read=receive_data_from_nest.communication_internal.lock_write
            )
        # creation of the object for TVB communication
        send_data_to_TVB = Send_TVB_Data(
            'nest_to_tvb_send'+str(id_spike_detector), path, level_log,
            communication_intern=Thread_communication,
            buffer_read=translation.communication_internal.buffer_write_data,
            status_read=translation.communication_internal.status_write,
            lock_read=translation.communication_internal.lock_write
            )
        path_to_files_send = [path + TVB_recev_file]

        # creation of the threads and run them
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
        raise Exception('Wrong number of MPI rank. The rank need to be 1 or 3')

    if id_translator == 1 and rank == 1:
        os.remove(path + '/nest/spike_detector.txt.unlock')
