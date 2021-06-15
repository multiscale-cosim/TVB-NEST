#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import logging
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('tvb').setLevel(logging.ERROR)
import tvb.simulator.lab as lab
import numpy.random as rgn
import numpy as np
from nest_elephant_tvb.Tvb.modify_tvb import Zerlaut as Zerlaut
from nest_elephant_tvb.Tvb.modify_tvb.Interface_co_simulation_parallel import Interface_co_simulation
from nest_elephant_tvb.Tvb.helper_function_zerlaut import ECOG,findVec
from nest_elephant_tvb.Tvb.wrapper_TVB import simulate_tvb
import json


def init(param_tvb_connection, param_tvb_coupling, param_tvb_integrator, param_tvb_model, param_tvb_monitor,
         cosim=None):
    """
    Initialise the simulator with parameter
    :param param_tvb_connection : parameters for the connection
    :param param_tvb_coupling : parameters for the coupling between nodes
    :param param_tvb_integrator : parameters of the integrator and the noise
    :param param_tvb_model : parameters for the models of TVB
    :param param_tvb_monitor : parameters for TVB monitors
    :param cosim : if use or not mpi
    :return: the simulator initialize
    """
    ## initialise the random generator
    rgn.seed(param_tvb_integrator['seed_init'] - 1)

    ## Model configuration
    if param_tvb_model['order'] == 1:
        model = Zerlaut.ZerlautAdaptationFirstOrder(variables_of_interest='E I W_e W_i'.split())
    elif param_tvb_model['order'] == 2:
        model = Zerlaut.ZerlautAdaptationSecondOrder(variables_of_interest='E I C_ee C_ei C_ii W_e W_i'.split())
    else:
        raise Exception('Bad order for the model')
    model.g_L = np.array(param_tvb_model['g_L'])
    model.E_L_e = np.array(param_tvb_model['E_L_e'])
    model.E_L_i = np.array(param_tvb_model['E_L_i'])
    model.C_m = np.array(param_tvb_model['C_m'])
    model.b_e = np.array(param_tvb_model['b_e'])
    model.a_e = np.array(param_tvb_model['a_e'])
    model.b_i = np.array(param_tvb_model['b_i'])
    model.a_i = np.array(param_tvb_model['a_i'])
    model.tau_w_e = np.array(param_tvb_model['tau_w_e'])
    model.tau_w_i = np.array(param_tvb_model['tau_w_i'])
    model.E_e = np.array(param_tvb_model['E_e'])
    model.E_i = np.array(param_tvb_model['E_i'])
    model.Q_e = np.array(param_tvb_model['Q_e'])
    model.Q_i = np.array(param_tvb_model['Q_i'])
    model.tau_e = np.array(param_tvb_model['tau_e'])
    model.tau_i = np.array(param_tvb_model['tau_i'])
    model.N_tot = np.array(param_tvb_model['N_tot'])
    model.p_connect_e = np.array(param_tvb_model['p_connect_e'])
    model.p_connect_i = np.array(param_tvb_model['p_connect_i'])
    model.g = np.array(param_tvb_model['g'])
    model.T = np.array(param_tvb_model['T'])
    model.P_e = np.array(param_tvb_model['P_e'])
    model.P_i = np.array(param_tvb_model['P_i'])
    model.K_ext_e = np.array(param_tvb_model['K_ext_e'])
    model.K_ext_i = np.array(0)
    model.tau_OU = np.array(param_tvb_model['tau_OU'])
    model.weight_noise = np.array(param_tvb_model['weight_noise'])
    model.external_input_ex_ex = np.array(param_tvb_model['excitatory_extern'])
    model.external_input_in_ex = np.array(param_tvb_model['excitatory_extern'])
    model.external_input_in_ex = np.array(0.0)
    model.external_input_in_in = np.array(0.0)
    model.state_variable_range['E'] = np.array(param_tvb_model['initial_condition']['E'])
    model.state_variable_range['I'] = np.array(param_tvb_model['initial_condition']['I'])
    if param_tvb_model['order'] == 2:
        model.state_variable_range['C_ee'] = np.array(param_tvb_model['initial_condition']['C_ee'])
        model.state_variable_range['C_ei'] = np.array(param_tvb_model['initial_condition']['C_ei'])
        model.state_variable_range['C_ii'] = np.array(param_tvb_model['initial_condition']['C_ii'])
    model.state_variable_range['W_e'] = np.array(param_tvb_model['initial_condition']['W_e'])
    model.state_variable_range['W_i'] = np.array(param_tvb_model['initial_condition']['W_i'])

    ## Connection
    nb_region = int(param_tvb_connection['nb_region'])
    tract_lengths = np.load(param_tvb_connection['path_distance'])
    weights = np.load(param_tvb_connection['path_weight'])
    if 'path_region_labels' in param_tvb_connection.keys():
        region_labels = np.loadtxt(param_tvb_connection['path_region_labels'], dtype=str)
    else:
        region_labels = np.array([], dtype=np.dtype('<U128'))
    if 'path_centers' in param_tvb_connection.keys():
        centers = np.loadtxt(param_tvb_connection['path_centers'])
    else:
        centers = np.array([])
    if 'orientation' in param_tvb_connection.keys() and param_tvb_connection['orientation']:
        orientation = []
        for i in np.transpose(centers):
            orientation.append(findVec(i, np.mean(centers, axis=1)))
        orientation = np.array(orientation)
    else:
        orientation = None
    if 'path_cortical' in param_tvb_connection.keys():
        cortical = np.load(param_tvb_connection['path_cortical'])
    else:
        cortical = None
    connection = lab.connectivity.Connectivity(number_of_regions=nb_region,
                                               tract_lengths=tract_lengths[:nb_region, :nb_region],
                                               weights=weights[:nb_region, :nb_region],
                                               region_labels=region_labels,
                                               centres=centers.T,
                                               cortical=cortical,
                                               orientations=orientation)
    # if 'normalised' in param_tvb_connection.keys() or param_tvb_connection['normalised']:
    #     connection.weights = connection.weights / np.sum(connection.weights, axis=0)
    connection.speed = np.array(param_tvb_connection['velocity'])

    ## Coupling
    coupling = lab.coupling.Linear(a=np.array(param_tvb_coupling['a']),
                                   b=np.array(0.0))

    ## Integrator
    # add gaussian noise to the noise of the model
    noise = lab.noise.Additive(
        nsig=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0]),
        ntau=0.0,
        noise_seed = param_tvb_integrator['seed']
    )
    noise.random_stream.seed(param_tvb_integrator['seed'])
    integrator = lab.integrators.HeunStochastic(noise=noise, dt=param_tvb_integrator['sim_resolution'])

    ## Monitors
    monitors = []
    if param_tvb_monitor['Raw']:
        monitors.append(lab.monitors.Raw())
    if param_tvb_monitor['TemporalAverage']:
        monitor_TAVG = lab.monitors.TemporalAverage(
            variables_of_interest=param_tvb_monitor['parameter_TemporalAverage']['variables_of_interest'],
            period=param_tvb_monitor['parameter_TemporalAverage']['period'])
        monitors.append(monitor_TAVG)
    if param_tvb_monitor['Bold']:
        monitor_Bold = lab.monitors.Bold(
            variables_of_interest=np.array(param_tvb_monitor['parameter_Bold']['variables_of_interest']),
            period=param_tvb_monitor['parameter_Bold']['period'])
        monitors.append(monitor_Bold)
    if param_tvb_monitor['ECOG']:
        volume = np.loadtxt(param_tvb_monitor['parameter_ECOG']['path_volume'])[:nb_region]  # volume of the regions
        monitors.append(ECOG().from_file(param_tvb_monitor['parameter_ECOG']['path'],
                                         param_tvb_monitor['parameter_ECOG']['scaling'],
                                         volume=volume
                                         ))
    if cosim is not None:
        # special monitor for MPI
        monitor_IO = Interface_co_simulation(
            id_proxy=cosim['id_proxy'],
            time_synchronize=cosim['time_synchronize']
        )
        monitors.append(monitor_IO)

    # initialize the simulator:
    simulator = lab.simulator.Simulator(model=model, connectivity=connection,
                                        coupling=coupling, integrator=integrator, monitors=monitors
                                        )
    simulator.configure()
    # save the initial condition
    np.save(param_tvb_monitor['path_result'] + '/step_init.npy', simulator.history.buffer)
    # end edit
    return simulator


def run_normal(path_parameter):
    with open(path_parameter + '/parameter.json') as f:
        parameters = json.load(f)
    begin = parameters['begin']
    end = parameters['end']
    results_path = parameters['result_path']
    simulate_tvb(init,results_path=results_path, begin=begin, end=end,
                 param_tvb_connection=parameters['param_tvb_connection'],
                 param_tvb_coupling=parameters['param_tvb_coupling'],
                 param_tvb_integrator=parameters['param_tvb_integrator'],
                 param_tvb_model=parameters['param_tvb_model'],
                 param_tvb_monitor=parameters['param_tvb_monitor'])

if __name__ == "__main__":
    import sys
    from wrapper_TVB_mpi import run_mpi

    if len(sys.argv) == 2:
        run_mpi(init,sys.argv[1])
    else:
        raise Exception('not good number of argument ')
