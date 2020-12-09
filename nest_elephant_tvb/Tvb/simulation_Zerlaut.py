#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import tvb.simulator.lab as lab
from tvb.contrib.cosimulation.cosimulator import CoSimulator
from tvb.contrib.cosimulation.co_sim_monitor import Coupling_co_sim
from tvb.datatypes.sensors import SensorsInternal
import numpy.random as rgn
import numpy as np
import nest_elephant_tvb.Tvb.modify_tvb.noise as my_noise
import nest_elephant_tvb.Tvb.modify_tvb.Zerlaut as Zerlaut
from nest_elephant_tvb.Tvb.helper_function_zerlaut import findVec
from nest_elephant_tvb.Tvb.TVB_tools import run_normal,run_mpi

def init(param_tvb_connection,param_tvb_coupling,param_tvb_integrator,param_tvb_model,param_tvb_monitor,cosim=None):
    '''
    Initialise the simulator with parameter
    :param param_tvb_connection : parameters for the connection
    :param param_tvb_coupling : parameters for the coupling between nodes
    :param param_tvb_integrator : parameters of the integrator and the noise
    :param param_tvb_model : parameters for the models of TVB
    :param param_tvb_monitor : parameters for TVB monitors
    :param cosim : if use or not mpi
    :return: the simulator initialize
    '''
    ## initialise the random generator
    rgn.seed(param_tvb_integrator['seed_init']-1)

    ## Model configuration
    if param_tvb_model['order'] == 1:
        model = Zerlaut.ZerlautAdaptationFirstOrder(variables_of_interest='E I W_e W_i'.split())
    elif param_tvb_model['order'] == 2:
        model = Zerlaut.ZerlautAdaptationSecondOrder(variables_of_interest='E I C_ee C_ei C_ii W_e W_i'.split())
    else:
        raise Exception('Bad order for the model')
    model.g_L=np.array(param_tvb_model['g_L'])
    model.E_L_e=np.array(param_tvb_model['E_L_e'])
    model.E_L_i=np.array(param_tvb_model['E_L_i'])
    model.C_m=np.array(param_tvb_model['C_m'])
    model.b_e=np.array(param_tvb_model['b_e'])
    model.a_e=np.array(param_tvb_model['a_e'])
    model.b_i=np.array(param_tvb_model['b_i'])
    model.a_i=np.array(param_tvb_model['a_i'])
    model.tau_w_e=np.array(param_tvb_model['tau_w_e'])
    model.tau_w_i=np.array(param_tvb_model['tau_w_i'])
    model.E_e=np.array(param_tvb_model['E_e'])
    model.E_i=np.array(param_tvb_model['E_i'])
    model.Q_e=np.array(param_tvb_model['Q_e'])
    model.Q_i=np.array(param_tvb_model['Q_i'])
    model.tau_e=np.array(param_tvb_model['tau_e'])
    model.tau_i=np.array(param_tvb_model['tau_i'])
    model.N_tot=np.array(param_tvb_model['N_tot'])
    model.p_connect=np.array(param_tvb_model['p_connect'])
    model.g=np.array(param_tvb_model['g'])
    model.T=np.array(param_tvb_model['T'])
    model.P_e=np.array(param_tvb_model['P_e'])
    model.P_i=np.array(param_tvb_model['P_i'])
    model.K_ext_e=np.array(param_tvb_model['K_ext_e'])
    model.K_ext_i=np.array(0)
    model.external_input_ex_ex=np.array(0.)
    model.external_input_ex_in=np.array(0.)
    model.external_input_in_ex=np.array(0.0)
    model.external_input_in_in=np.array(0.0)
    model.state_variable_range['E'] =np.array( param_tvb_model['initial_condition']['E'])
    model.state_variable_range['I'] =np.array( param_tvb_model['initial_condition']['I'])
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
             orientation.append(findVec(i,np.mean(centers,axis=1)))
        orientation = np.array(orientation)
    else:
       orientation = None
    if 'path_cortical' in param_tvb_connection.keys():
        cortical = np.load(param_tvb_connection['path_cortical'])
    else:
        cortical=None
    connection = lab.connectivity.Connectivity(number_of_regions=nb_region,
                                               tract_lengths=tract_lengths[:nb_region,:nb_region],
                                               weights=weights[:nb_region,:nb_region],
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
    noise = my_noise.Ornstein_Ulhenbeck_process(
        tau_OU=param_tvb_integrator['tau_OU'],
        mu=np.array(param_tvb_integrator['mu']).reshape((7,1,1)),
        nsig=np.array(param_tvb_integrator['nsig']),
        weights=np.array(param_tvb_integrator['weights']).reshape((7,1,1))
    )
    noise.random_stream.seed(param_tvb_integrator['seed'])
    integrator = lab.integrators.HeunStochastic(noise=noise,dt=param_tvb_integrator['sim_resolution'])
    # integrator = lab.integrators.HeunDeterministic()

    ## Monitors
    monitors =[]
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
    if param_tvb_monitor['SEEG']:
        sensor = SensorsInternal().from_file(param_tvb_monitor['parameter_SEEG']['path'])
        projection_matrix = param_tvb_monitor['parameter_SEEG']['scaling_projection']/np.array(
            [np.linalg.norm(np.expand_dims(i, 1) - centers[:, cortical], axis=0) for i in sensor.locations])
        np.save(param_tvb_monitor['path_result']+'/projection.npy',projection_matrix)
        monitors.append(lab.monitors.iEEG.from_file(
            param_tvb_monitor['parameter_SEEG']['path'],
            param_tvb_monitor['path_result']+'/projection.npy'))
    if cosim is not None:
        # special monitor for MPI
        simulator = CoSimulator(
                                voi = np.array([0]), # coupling with Excitatory firing rate
                                synchronization_time=cosim['time_synchronize'],
                                co_monitor = (Coupling_co_sim( coupling = coupling ),),
                                proxy_inds=np.asarray(cosim['id_proxy'], dtype=np.int),
                                model = model, connectivity = connection,
                                coupling = coupling, integrator = integrator, monitors = monitors
                                )
    else:
        #initialize the simulator:
        simulator = lab.simulator.Simulator(model = model, connectivity = connection,
                                            coupling = coupling, integrator = integrator, monitors = monitors
                                        )
    simulator.configure()
    # save the initial condition
    np.save(param_tvb_monitor['path_result']+'/step_init.npy',simulator.history.buffer)
    # end edit
    return simulator


if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        if sys.argv[1] == '0': # run only tvb without mpi
            run_normal(init,sys.argv[2])
        elif sys.argv[1] == '1': # run tvb in co-simulation configuration
            run_mpi(init,sys.argv[2])
        else:
            raise Exception('bad option of running')
    else:
        raise Exception('not good number of argument ')
