#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import os
# PARAMETERS BY DEFAULT FOR TESTING THE SIMULATION
path = os.path.dirname(os.path.realpath(__file__))+"/../example/parameter/data_mouse/"

# ALL commented parameters are linked parameter manage by parameters_manager.py
# For the exploration of parameters never use the same name two times in the dictionary param

#parameter for the cosimulations and parameters of the simulations
param_co_simulation={
    # boolean for check if there are or not co-simulation
    'co-simulation':True,
    # number of MPI process for nest
    # select if nest is use or not
    'nb_MPI_nest':1,
    # save or not nest( result with MPI )
    'record_MPI':False,
    # id of region simulate by nest
    'id_region_nest':[29, 81],
    # time of synchronization between node
    'synchronization':3.5,
    # level of log : debug 0, info 1, warning 2, error 3, critical 4
    'level_log':1,
    # if running in cluster:
    'cluster':False
}

#parameter simulators
param_nest={
    # Resolution of the simulation (in ms).
    'sim_resolution': 0.1,
    # Masterseed for NEST and NumPy.
    'master_seed': 46,
    # Number of threads per MPI process.
    'total_num_virtual_procs': 10,
    # If True, data will be overwritten,
    # If False, a NESTError is raised if the files already exist.
    'overwrite_files': True,
    # Print the time progress, this should only be used when the simulation
    # is run on a local machine.
    'print_time': True,
    #verbosity of Nest :M_ALL=0, M_DEBUG=5, M_STATUS=7, M_INFO=10, M_WARNING=20, M_ERROR=30, M_FATAL=40, M_QUIET=100
    'verbosity':20
}

#parameter for nest simulation
param_nest_topology={
    # number of region of simulated in the brain
    'nb_region':104,
    # Number of neurons by region
    'nb_neuron_by_region':int(1e4),
    # Percentage of inhibitory neurons
    'percentage_inhibitory':0.2,
    # Type of neuron
    'neuron_type':'aeif_cond_exp',
    # Parameter of excitatory neuron (different to default value)
    # Some parameters are not use in TVB
    'param_neuron_excitatory': {
        'C_m':200.0,
        't_ref':5.0,
        'V_reset':-64.5,
        'E_L':-64.5,
        'g_L':10.0,
        'I_e':0.0,
        'a':0.0,
        'b':1.0,
        'Delta_T':2.0,
        'tau_w':500.0,
        'V_th':-50.0,
        'E_ex':0.0,
        'tau_syn_ex':5.0,
        'E_in':-80.0,
        'tau_syn_in':5.0,
    },
    # Parameter for inhibitory neurons
    #  Some parameters are not use in TVB
    # Not implementation of the exploration parameter for inhibitory neurons
    'param_neuron_inhibitory': {
        'C_m':200.0,
        't_ref':5.0,
        'V_reset':-65.0,
        'E_L':-65.,
        'g_L':10.0,
        'I_e':0.0,
        'a':0.0,
        'b':0.0,
        'Delta_T':0.5,
        'tau_w':1.0,
        'V_th':-50.0,
        'E_ex':0.0,
        'tau_syn_ex':5.0,
        'E_in':-80.0,
        'tau_syn_in':5.0,
    },
    # Mean of external input
    'mean_I_ext':0.0,
    # Standard deviation of the external input
    'sigma_I_ext':0.0,
    # Standard deviation of initial condition
    'sigma_V_0':10.,
    # Mean deviation of initial condition
    'mean_w_0':10.0,
}

param_nest_connection={
    #file for connection homogeneous
    'path_homogeneous':path+'/connection_homogeneous_',
    #file for connection heterogenous
    'path_heterogeneous':path+'/connection_heterogeneous_',
    # weigth in the population from excitatory neurons
    'weight_local':1.0,
    # ratio between excitatory weight and inhibitory weight
    'g':5.0,
    #probability inside the region
    'p_connect':0.05,
    # number of external synapse:
    'nb_external_synapse':115,
    # path for the connectivity matrix (normalise in order to sum of input for region egual 1)
    'path_weight':path+'/weights.npy',
    # path for the distance matrix
    'path_distance':path+'/distance.npy',
    # path for the center of the node
    'path_centers':path+'/centres.txt',
    # path for the distance matrix
    'path_region_labels':path+'/region_labels.txt',
    #velocity of transmission in m/s
    'velocity':3.0,
    #Weight between region
    'weight_global': 1.0,
}

param_nest_background={
    #define if the simulation use or not a poisson generator
    'poisson':True,
    # rate of poisson
    'rate_ex':2.0,
    'rate_in':0.0,
    #the weight on the connection
    # 'weight_poisson':param_nest_connection['weight_local'],
    #define if the simulation have or not noise
    'noise':False,
    # Mean of the noise in pA
    'mean_noise':0.0,
    # Standard deviation of the noise
    'sigma_noise':400.0,
    #the weight on the connection
    'weight_noise':1.0,
    #stimulus
    'stimulus':False,
    #stimulus amplitude
    'stimulus_amplitude':0.0,
    #stimulus time to start
    'stimulus_start':0.0,
    #stimulus duration
    'stimulus_duration':0.0,
    #stimulus populatin target
    'stimulus_target':0,
    #multimeter => ask a lot of memory
    'multimeter': True,
    'multimeter_list':{'pop_1_ex_VM':(['V_m'],0,10),'pop1_ex_W':(['w'],0,10),'pop_1_in_VM':(['V_m'],800,810),'pop1_in_W':(['w'],800,810)},
    'record_spike': True,
    'record_spike_list':{'pop_1_ex':(0,799),'pop_2_ex':(1000,1799),'pop_1_in':(800,999),'pop_2_in':(1800,1999)},
}

# parameter TVB for the connection between node
param_tvb_connection={
    # path for the connectivity matrix (normalise in order to sum of input for region egual 1)
    # 'path_weight':param_nest_connection['path_distance'],
    # path for the distance matrix
    # 'path_distance':param_nest_connection['path_distance'],
    # number of region
    # 'nb_region': param_nest_topology['nb_region']
    # velocity of transmission in m/s
    #'velocity': param_nest_connection['velocity']
}

# parameter TVB for the LINEAR coupling
param_tvb_coupling={
    # The global scaling of the connection weights
    # 'a' : param_nest_connection['weight_global']
}

# parameter TVB for the STOCHASTIC HEUN integrator
param_tvb_integrator = {
    # integration step
    # 'sim_resolution': param_nest['sim_resolution']
    # seed for the random generator
    # 'master_seed': param_nest['master_seed']-1
    # seed for the initialisation of the history
    # 'master_seed_init': param_nest['master_seed']-2
    # parameters for a special noise
    'tau_OU':20.0,
    'mu':[2.0,0.0,0.,0.0,0.0,0.0,0.0],
    'nsig':[2.0,0.,0.,0.,0.,0.,0.],
    'weights':[1.e-2,0.,0.,0.,0.,0.,0.],
}

#parameter for the model of the node : ZERLAUT model / Mean field AdEX
param_tvb_model={
    #order of the model
    'order':2,
    # 'g_L':param_nest_topology['param_neuron_excitatory']['g_L']
    # 'E_L_e':param_nest_topology['param_neuron_excitatory']['E_L']
    # 'E_L_i':param_nest_topology['param_neuron_inhibitory']['E_L']
    # 'C_m':param_nest_topology['param_neuron_excitatory']['C_m']
    # 'b_e':param_nest_topology['param_neuron_excitatory']['b']
    # 'a_e':param_nest_topology['param_neuron_excitatory']['a']
    # 'b_i':param_nest_topology['param_neuron_inhibitory']['b']
    # 'a_i':param_nest_topology['param_neuron_inhibitory']['a']
    # 'tau_w_e':param_nest_topology['param_neuron_excitatory']['tau_w']
    # 'tau_w_i':param_nest_topology['param_neuron_inhibitory']['tau_w']
    # 'E_e':param_nest_topology['param_neuron_excitatory']['E_ex']
    # 'E_i':param_nest_topology['param_neuron_excitatory']['E_in']
    # 'Q_e':param_nest_connection['weight_local']
    # 'Q_i':param_nest_connection['weight_local']*param_nest_connection['g']
    # 'tau_e':param_nest_topology['param_neuron_excitatory']['tau_syn_ex']
    # 'tau_i':param_nest_topology['param_neuron_excitatory']['tau_syn_in']
    # 'N_tot':param_nest_topology['nb_neuron_by_region']
    # 'p_connect':param_nest_connection['p_connect']
    # 'g':param_nest_topology['percentage_inhibitory']
    # 'K_ext_e':param_nest_connection['nb_external_synapse']
    # Time constant of the model
    'T':20.0,
    # Polynome for excitatory neurons | WARNING :should be change when the parameter of neurons change)
    'P_e':[-0.05059317,  0.0036078 ,  0.01794401,  0.00467008,  0.00098553,  0.0082953 , -0.00985289, -0.02600252, -0.00274499, -0.01051463],
    # Polynome for inhibitory neurons | WARNING: should be change when the parameter of neurons change)
    'P_i':[-5.96722865e-02,  7.15675508e-03,  4.28252163e-03,  9.25089702e-03,  1.16632197e-06, -1.00659310e-02,  3.89257235e-03,  4.45787751e-04,  4.20050937e-03,  4.37359879e-03],
    # initial condition, should be simmilar than nest
    'initial_condition':{"E": [0.0, 0.0], "I": [0.0, 0.0], "C_ii": [0.0, 0.0], "W_e": [0.0, 0.0], "C_ee": [0.0, 0.0], "C_ei": [0.0, 0.0], "W_i": [0.0, 0.0]},
}

# parameter TVB for the monitors
param_tvb_monitor={
    # the time of simulation in each file
    'save_time': 20.0,
    # use or not the Raw monitor
    'Raw':True,
    # Use or not the Temporal Average Monitor
    'TemporalAverage':False,
    # Parameter for Temporal Average Monitor
    'parameter_TemporalAverage':{
        'variables_of_interest':[0,1,2,3],
        # 'period': param_nest['sim_resolution']*10.0 # 1s assuming the step size is 0.1 ms
    },
    # Use or not the Bold Monitor
    'Bold':False,
    # Paramter for the Bold Monitor
    'parameter_Bold':{
        'variables_of_interest':[0],
        # 'period':param_nest['sim_resolution']*20000.0 # 20 min assuming the step size is 0.1 ms
    },
    'SEEG':False
}

# Parameters for the translator Nest to TVB
param_TR_nest_to_tvb={
    # 'init': path of the initialisation of the translation if not the run exploration will create it
    # 'resolution': param_nest['sim_resolution']
    # 'synch': param_co_simulation['synchronization']
    # 'width': param_zerlaut['T']
    # 'nb_neurons' : param_nest_topology['nb_neuron_by_region'] * (1-param_nest_topology['percentage_inhibitory']) # number of excitatory neurons
    # 'level_log': param_co_simulation['level_log']
}

# Parameters for the translator TVB to Nest
param_TR_tvb_to_nest={
    # percentage of shared rate between neurons of the same region
    'percentage_shared': 0.5,
    # 'seed':param_nest['master_seed']-3 # -3 because -1 and -2 is use by the simulation of TVB
    # 'nb_synapses' : param_nest_connection['nb_external_synapse'] # number of external synapses
    # 'init': path of the initialisation of the translation if not the run exploration will create it
    # 'level_log': param_co_simulation['level_log']
    'function_select':2
}

# Parameters for the module of saving by MPI
param_record_MPI={
    # save step
    'save_step': 0,
    # 'init': path of the initialisation of the translation if not the run exploration will create it
    # 'resolution': param_nest['sim_resolution']
    # 'synch': param_co_simulation['synchronization']
    # 'level_log': param_co_simulation['level_log']
}

