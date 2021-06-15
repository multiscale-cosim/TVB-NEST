#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import logging
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('tvb').setLevel(logging.ERROR)
import numpy as np


def simulate_tvb(init,results_path, begin, end, param_tvb_connection, param_tvb_coupling,
                 param_tvb_integrator, param_tvb_model, param_tvb_monitor):
    '''
    simulate TVB with zerlaut simulation
    :param results_path: the folder to save the result
    :param begin: the starting point of record  WARNING : not used
    :param end: the ending point of record
    :param param_tvb_connection : parameters for the connection
    :param param_tvb_coupling : parameters for the coupling between nodes
    :param param_tvb_integrator : parameters of the integrator and the noise
    :param param_tvb_model : parameters for the models of TVB
    :param param_tvb_monitor : parameters for TVB monitors
    :return: simulation
    '''
    param_tvb_monitor['path_result'] = results_path + '/tvb/'
    simulator = init(param_tvb_connection, param_tvb_coupling, param_tvb_integrator, param_tvb_model, param_tvb_monitor)
    run_simulation(simulator, end, param_tvb_monitor)


def run_simulation(simulator, times, parameter_tvb):
    '''
    run a simulation
    :param simulator: the simulator already initialize
    :param times: the time of simulation
    :param parameter_tvb: the parameter for the simulator
    '''
    # check how many monitor it's used
    nb_monitor = parameter_tvb['Raw'] + parameter_tvb['TemporalAverage'] + parameter_tvb['Bold'] + parameter_tvb['ECOG']
    # initialise the variable for the saving the result
    save_result = []
    for i in range(nb_monitor):
        save_result.append([])
    # run the simulation
    count = 0
    for result in simulator(simulation_length=times):
        for i in range(nb_monitor):
            if result[i] is not None:
                save_result[i].append(result[i])
        # save the result in file
        if result[0][0] >= parameter_tvb['save_time'] * (count + 1):  # check if the time for saving at some time step
            print('simulation time :' + str(result[0][0]) + '\r')
            np.save(parameter_tvb['path_result'] + '/step_' + str(count) + '.npy', save_result)
            save_result = []
            for i in range(nb_monitor):
                save_result.append([])
            count += 1
    # save the last part
    np.save(parameter_tvb['path_result'] + '/step_' + str(count) + '.npy', save_result)

