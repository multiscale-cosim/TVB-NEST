#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import os
import json
import time
import numpy as np
from nest_elephant_tvb.utils import create_logger
from nest_elephant_tvb.transformation.simulator_IO.Nest_IO import ConsumerNestData
from nest_elephant_tvb.transformation.simulator_IO.TVB_IO import ProducerTVBData
from nest_elephant_tvb.transformation.transformation_function.translation_function import TransformationSpikeRate
from nest_elephant_tvb.transformation.communication.internal_mpi import MPICommunication
from nest_elephant_tvb.transformation.communication.internal_thread import ThreadCommunication
from timer.Timer import Timer

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print('incorrect number of arguments')
        exit(1)

    rank = MPI.COMM_WORLD.Get_rank()
    if rank == 0:
        timer_master = Timer(1, 5)
        timer_master.start(0)
    # Parse arguments
    path = sys.argv[1]  # path of the simulation
    id_transformer = int(sys.argv[2])  # index of the transformer

    # take the parameters and instantiate objects
    with open(path + '/parameter.json') as f:
        parameters = json.load(f)
    id_proxy = parameters['param_co_simulation']['id_region_nest']
    param = parameters['param_TR_nest_to_tvb']
    level_log = param['level_log']
    logger = create_logger(path, 'nest_to_tvb_' + str(id_transformer), level_log)

    if rank == 0:
        timer_master.change(0, 0)
    while not os.path.exists(path + '/nest/spike_detector.txt.unlock'):
        logger.info("spike detector ids not found yet, retry in 1 second")
        time.sleep(1)
    spike_detector = np.loadtxt(path + '/nest/spike_detector.txt', dtype=int)
    # case of one spike detector
    try:
        spike_detector = np.array([int(spike_detector)])
    except:
        pass

    id_spike_detector = spike_detector[id_transformer]
    file_spike_detector = "/transformation/spike_detector/" + str(id_spike_detector) + ".txt"
    TVB_recev_file = "/transformation/send_to_tvb/" + str(id_proxy[id_transformer]) + ".txt"
    id_spike_detector = os.path.splitext(os.path.basename(path + file_spike_detector))[0]

    if rank == 0:
        timer_master.change(0, 0)
    if MPI.COMM_WORLD.Get_size() == 3:  # MPI internal communication
        if rank == 0:  # communication with Nest
            receive_data_from_nest = ConsumerNestData(
                'nest_to_tvb_receive' + str(id_spike_detector), path, level_log,
                communication_intern=MPICommunication, buffer_r_w=[2, 0])
            path_to_files_receive = [path + file_spike_detector]
            if rank == 0:
                timer_master.change(0, 0)
            receive_data_from_nest.run(path_to_files_receive)
        elif rank == 1:  # communication with TVB
            send_data_to_TVB = ProducerTVBData(
                'nest_to_tvb_send' + str(id_spike_detector), path, level_log,
                communication_intern=MPICommunication, sender_rank=2, buffer_r_w=[2, 0])
            path_to_files_send = [path + TVB_recev_file]
            send_data_to_TVB.run(path_to_files_send)
        elif rank == 2:  # transformation from spike to rate
            transformation = TransformationSpikeRate(
                id_transformer, param,
                'nest_to_tvb_transform' + str(id_spike_detector), path, level_log,
                communication_intern=MPICommunication, receiver_rank=1, buffer_r_w=[2, 0])
            transformation.run(None)
        else:
            raise Exception('too much rank')
    elif MPI.COMM_WORLD.Get_size() == 1:  # Thread internal communication
        from threading import Thread
        import numpy as np

        # creation of the object for Nest communication
        receive_data_from_nest = ConsumerNestData(
            'nest_to_tvb_receive' + str(id_spike_detector), path, level_log,
            communication_intern=ThreadCommunication,
            buffer_write_status=np.ones((1, 1), dtype=int) * -2,
            buffer_write_shape=(1000000 * 3, 1),
        )
        path_to_files_receive = [path + file_spike_detector]
        # creation of the object for the transformation from rate to spike
        transformation = TransformationSpikeRate(
            id_transformer, param,
            'nest_to_tvb_transformer' + str(id_spike_detector), path, level_log,
            communication_intern=ThreadCommunication,
            buffer_write_status=np.ones(1) * -2,
            buffer_write_shape=(2, int(param['synch'] / param['resolution'])),
            buffer_read=receive_data_from_nest.communication_internal.buffer_write_data,
            status_read=receive_data_from_nest.communication_internal.status_write,
            lock_read=receive_data_from_nest.communication_internal.lock_write
        )
        # creation of the object for TVB communication
        send_data_to_TVB = ProducerTVBData(
            'nest_to_tvb_send' + str(id_spike_detector), path, level_log,
            communication_intern=ThreadCommunication,
            buffer_read=transformation.communication_internal.buffer_write_data,
            status_read=transformation.communication_internal.status_write,
            lock_read=transformation.communication_internal.lock_write
        )
        path_to_files_send = [path + TVB_recev_file]
        if rank == 0:
            timer_master.change(0, 0)

        # creation of the threads and run them
        th_receive = Thread(target=receive_data_from_nest.run, args=(path_to_files_receive,))
        th_transformation = Thread(target=transformation.run, args=(None,))
        th_send = Thread(target=send_data_to_TVB.run, args=(path_to_files_send,))
        th_receive.start()
        th_transformation.start()
        th_send.start()
        th_transformation.join()
        th_receive.join()
        th_send.join()
    else:
        raise Exception('Wrong number of MPI rank. The rank need to be 1 or 3')

    if rank == 0:
        timer_master.change(0, 0)
    if id_transformer == 1 and rank == 1:
        os.remove(path + '/nest/spike_detector.txt.unlock')
    if rank == 0:
        timer_master.stop(0)
        timer_master.save(path + "/timer_" + logger.name + '.npy')
