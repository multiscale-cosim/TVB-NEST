import numpy as np

path ="/home/kusch/Documents/project/co_simulation/co-simulation_mouse/nest_elephant_tvb/parameter/data_mouse/"

param_co_simulation={
    'co-simulation':False,
    'nb_MPI_nest':1,
    'nb_MPI_TVB':0,
    'record_MPI':False,
    'nb_node':1,
}

#parameter simulators
param_nest={
    # Resolution of the simulation (in ms).
    'sim_resolution': 0.1,
    # Masterseed for NEST and NumPy.
    'master_seed': 46,
    # Number of threads per MPI process.
    'total_num_virtual_procs': 16,
    # If True, data will be overwritten,
    # If False, a NESTError is raised if the files already exist.
    'overwrite_files': True,
    # Print the time progress, this should only be used when the simulation
    # is run on a local machine.
    'print_time': True,
    #verbosity of Nest :M_ALL=0, M_DEBUG=5, M_STATUS=7, M_INFO=10, M_WARNING=20, M_ERROR=30, M_FATAL=40, M_QUIET=100
    'verbosity':20
}

# WARNING TVB use also some parameters of nest
param_tvb={
    # the time of simulation in each file
    'save_time': 2000.0,
    # use or not the Raw monitor
    'Raw':False,
    # Use or not the Temporal Average Monitor
    'TemporalAverage':False,
    # Parameter for Temporal Average Monitor
    'parameter_TemporalAverage':{
        'variables_of_interest':[0,1,2,3],
        'period':param_nest['sim_resolution']*10.0
    },
    # Use or not the Bold Monitor
    'Bold':True,
    # Paramter for the Bold Monitor
    'parameter_Bold':{
        'variables_of_interest':[0],
        'period':param_nest['sim_resolution']*20000.0
    }
}

#parameter for nest simulation
param_topology={
    'nb_region':10,
    # Number of neurons by region
    'nb_neuron_by_region':10000,
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
        'b':50.0,
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
    'sigma_V_0':0.,
    # Mean deviation of initial condition
    'mean_w_0':0.0,
}

param_connection={
    #file for connection homogeneous
    'path_homogeneous':path+'/connection_homogeneous_',
    #file for connection heterogenous
    'path_heterogeneous':path+'/connection_heterogeneous_',
    # weigth in the population from excitatory neurons
    'weight_local':1.0,
    # ratio between excitatory weight and inhibitory weight
    'g':2.5,
    #probability inside the region
    'p_connect':0.05,
    # number of external synapse:
    'nb_external_synapse':400,
    # path for the connectivity matrix (normalise in order to sum of input for region egual 1)
    'path_weight':path+'/weight.npy',
    # path for the distance matrix
    'path_distance':path+'/distance.npy',
    #velocity of transmission
    'velocity':3.0,
    #Weight between region
    'weight_global': 1.0,
}

param_background={
    #define if the simulation use or not a poisson generator
    'poisson':True,
    # rate of poisson
    'rate_ex':400.0*1.0e-3+2.0*140,
    'rate_in':200.0*1e-3+0.0*140,
    #the weight on the connexion
    'weight_poisson':param_connection['weight_local'],
    #define if the simulation have or not noise
    'noise':False,
    # Mean of the noise in pA
    'mean_noise':0.0,
    # Standard deviation of the noise
    'sigma_noise':400.0,
    #the weight on the connexion
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
    'multimeter':False
}

#parameter for tvb
param_zerlaut={
    #order of the model
    'order':2,
    # Time constant of the model
    'T':20.0,
    # Polynome for excitatory neurons | WARNING :should be change when the parameter of neurons change)
    'P_e':[-0.0498, 0.00506, -0.025, 0.0014, -0.00041, 0.0105, -0.036, 0.0074, 0.0012, -0.0407],
    # Polynome for inhibitory neurons | WARNING: should be change when the parameter of neurons change)
    'P_i':[-0.0514, 0.004, -0.0083, 0.0002, -0.0005, 0.0014, -0.0146, 0.0045, 0.0028, -0.0153],
    # initial condition, should be simmilar than nest #TODO
    'initial_condition':{"E": [0.0, 0.0], "I": [0., 0.], "C_ii": [0.0, 0.0], "W_e": [0.0, 0.0], "C_ee": [0.0, 0.0], "C_ei": [0.0, 0.0], "W_i": [0.0, 0.0]},
    # Should be link with noise in Nest #TODO
    'noise_parameter':{
        'nsig':[5e-09, 5e-09, 0.0, 0.0, 0.0, 0.0, 0.0],
        'ntau':0.0,
    },
}
