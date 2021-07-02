#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.launcher.run_exploration import run_exploration_2D
import numpy as np
from timer import parameter


def run_exploration(path, trial, begin, end, nb_neurons):
    """
    run co-simulation with different number of neurons
    :param path: path of result
    :param trial: index of trial
    :param begin: start recording
    :param end: ending recording
    :param nb_neurons: number of neurons
    :return:
    """
    parameter.param_nest_topology['nb_neuron_by_region'] = nb_neurons
    run_exploration_2D(path + '/' + str(nb_neurons) + '/' + str(trial) + '/', parameter,
                       {'g': np.arange(parameter.param_nest_connection['g'],
                                       parameter.param_nest_connection['g'] + 0.2, 0.5),
                        'mean_I_ext': [0.0]}, begin, end)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 6:
        run_exploration(sys.argv[1], int(sys.argv[2]), float(sys.argv[3]),
                        float(sys.argv[4]), int(sys.argv[5]))
    elif len(sys.argv) == 1:
        run_exploration('./test_file/neuron/', 0, 0.0, 1000.0, 1)
    else:
        print('missing argument')
