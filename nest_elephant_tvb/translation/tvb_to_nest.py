#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import os
import json
import time
import numpy as np
from nest_elephant_tvb.utils import create_logger
from nest_elephant_tvb.translation.simulator_IO.Nest_IO import ProducerDataNest
from nest_elephant_tvb.translation.simulator_IO.TVB_IO import ConsumerTVBData
from nest_elephant_tvb.translation.simulator_IO.translation_function import TranslationRateSpike
from nest_elephant_tvb.translation.communication.internal_mpi import MPICommunication
from nest_elephant_tvb.translation.communication.internal_thread import ThreadCommunication


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print('missing argument')
        exit(1)

    # Parse arguments
    path = sys.argv[1]  # path of the simulation
    id_translator = int(sys.argv[2])  # index of the translator

    # take the parameters and instantiate objects
    with open(path+'/parameter.json') as f:
        parameters = json.load(f)
    param = parameters['param_TR_tvb_to_nest']
    level_log = param['level_log']
    id_proxy = parameters['param_co_simulation']['id_region_nest']
    logger = create_logger(path, 'tvb_to_nest_'+str(id_translator), level_log)
    rank = MPI.COMM_WORLD.Get_rank()

    while not os.path.exists(path + '/nest/spike_generator.txt.unlock'):
        logger.info("spike generator ids not found yet, retry in 1 second")
        time.sleep(1)
    spike_generator = np.loadtxt(path + '/nest/spike_generator.txt', dtype=int)
    # case of one spike detector
    try:
        if len(spike_generator.shape) < 2:
            spike_generator = np.expand_dims(spike_generator, 0)
    except:
        pass

    logger.info("spike_generator : "+str(spike_generator))
    id_first_spike_detector = spike_generator[id_translator][0]
    nb_spike_generator = len(spike_generator[id_translator])

    if MPI.COMM_WORLD.Get_size() == 3:  # MPI internal communication
        if rank == 0:  # communication with Nest
            send_data_to_Nest = ProducerDataNest(
                id_first_spike_detector,
                'tvb_to_nest_sender' + str(id_first_spike_detector), path, level_log,
                communication_intern=MPICommunication, buffer_r_w=[0, 2])
            #  Create the port, file and set unlock for receiver
            path_to_files_sends = []
            for i in range(nb_spike_generator):
                # write file with port and unlock
                path_to_files_send = os.path.join(path + "/translation/spike_generator/",
                                                  str(id_first_spike_detector+i) + ".txt")
                path_to_files_sends.append(path_to_files_send)
            send_data_to_Nest.run(path_to_files_sends)
        elif rank == 1:  # communication with TVB
            receive_data_to_TVB = ConsumerTVBData(
                'tvb_to_nest_receiver'+str(id_first_spike_detector), path, level_log,
                communication_intern=MPICommunication, receiver_rank=2,
                buffer_r_w=[0, 2])
            path_to_files_receive = [path+"/translation/receive_from_tvb/"+str(id_proxy[id_translator])+".txt"]
            receive_data_to_TVB.run(path_to_files_receive)
        elif rank == 2:  # translation from rate to spike
            translate_rate_to_spike = TranslationRateSpike(
                id_translator, param, nb_spike_generator,
                'tvb_to_nest_translate' + str(id_first_spike_detector), path, level_log,
                communication_intern=MPICommunication,
                sender_rank=1, buffer_r_w=[0, 2])
            translate_rate_to_spike.run(None)
        else:
            raise Exception('too much rank')
    elif MPI.COMM_WORLD.Get_size() == 1:  # Thread internal communication
        from threading import Thread
        import numpy as np
        # creation of the object for TVB communication
        receive_data_to_TVB = ConsumerTVBData(
            'tvb_to_nest_receiver'+str(id_first_spike_detector), path, level_log,
            communication_intern=ThreadCommunication,
            buffer_write_status=np.ones(1)*-2,
            buffer_write_shape=(2, 2),
            )
        path_to_files_receive = [path+"/translation/receive_from_tvb/"+str(id_proxy[id_translator])+".txt"]
        # creation of the object for the traner Neurosciences & Philosophslation from rate to spike
        translate_rate_to_spike = TranslationRateSpike(
            id_translator, param, nb_spike_generator,
            'tvb_to_nest_translate' + str(id_first_spike_detector), path, level_log,
            communication_intern=ThreadCommunication,
            buffer_write_status=np.ones((1, 1), dtype=np.int)*-2,
            buffer_write_shape=(1000000 * 3, 1),
            buffer_read=receive_data_to_TVB.communication_internal.buffer_write_data,
            status_read=receive_data_to_TVB.communication_internal.status_write,
            lock_read=receive_data_to_TVB.communication_internal.lock_write
            )
        # creation of the object for Nest communication
        send_data_to_Nest = ProducerDataNest(
            id_first_spike_detector,
            'tvb_to_nest_sender' + str(id_first_spike_detector), path, level_log,
            communication_intern=ThreadCommunication,
            buffer_read=translate_rate_to_spike.communication_internal.buffer_write_data,
            status_read=translate_rate_to_spike.communication_internal.status_write,
            lock_read=translate_rate_to_spike.communication_internal.lock_write
            )
        path_to_files_sends = []
        for i in range(nb_spike_generator):
            # write file with port and unlock
            path_to_files_send = os.path.join(path + "/translation/spike_generator/",
                                              str(id_first_spike_detector + i) + ".txt")
            path_to_files_sends.append(path_to_files_send)

        # creation of the threads and run them
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
    # remove the locker file
    if id_translator == 1 and rank == 1:
        os.remove(path + '/nest/spike_generator.txt.unlock')
