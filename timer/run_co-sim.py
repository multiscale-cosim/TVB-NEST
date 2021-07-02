#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from nest_elephant_tvb.launcher.run_exploration import run_exploration_2D
import numpy as np
from timer import parameter


def run_exploration(path, begin, end):
    """
    test co-simulation and parameters
    :param path: path for the result
    :param begin: start recording
    :param end: end recording
    :return:
    """
    # run one simulation for testing everything
    run_exploration_2D(path, parameter, {'g': np.arange(parameter.param_nest_connection['g'],
                                                        parameter.param_nest_connection['g'] + 0.2, 0.5),
                                         'mean_I_ext': [0.0]}, begin, end)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 4:
        run_exploration(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]))
    elif len(sys.argv) == 1:
        run_exploration('./test_file/benchmark_paper_ebrains/0.1/10/1/1/0/_g_1.0_mean_I_ext_0.0/', 0.0, 1000.0)
    else:
        print('missing argument')
