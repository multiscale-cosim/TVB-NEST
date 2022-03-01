#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np


def min_delay_respect(param):
    """
    check if the min delay is respected
    :param param: parameter of the simulation
    :return: (true if the delay is correct, min delay)
    """
    time_syn = param['param_co_simulation']["synchronization"] / param['param_nest']["sim_resolution"]
    delays = np.load(param['param_nest_connection']["path_distance"]) / param['param_nest_connection']["velocity"]
    ids = param['param_co_simulation']["id_region_nest"]

    delay_proxy = delays[ids, :]
    delay_proxy = delay_proxy[:, ids]
    min_delay = -np.min(delay_proxy, initial=np.Inf, where=delay_proxy != 0.0)
    if min_delay == -np.Inf:
        min_delay = np.iinfo(np.int32).min
    else:
        min_delay = int(-np.min(delay_proxy, initial=np.Inf, where=delay_proxy != 0.0))
    return time_syn <= -min_delay, -min_delay


if __name__ == '__main__':
    import os

    path = os.path.dirname(os.path.realpath(__file__)) + "/parameter/data_mouse/"
    param = {'param_co_simulation': {'synchronization': 1.7, 'id_region_nest': [26, 76]},
             'param_nest_connection': {'path_distance': path + '/distance.npy', 'velocity': 3.0},
             'param_nest': {"sim_resolution": 0.1, }}
    respect, min_delay = min_delay_respect(param)
    print(respect, min_delay)
