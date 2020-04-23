import numpy as np

path ="/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/nest_elephant_tvb/parameter/data_mouse/"

#parameter for the cosimulations and parameters of the simulations
param_co_simulation={
    # boolean for check if there are or not co-simulation
    'co-simulation':False,
    # number of MPI process for nest (need to be equals to  param_nest['total_num_virtual_procs']
    # select if nest is use or not
    'nb_MPI_nest':1,
    # select if nest is use or not
    'nb_MPI_TVB':0,
    # save or not nest( result with MPI (not yet implemented)
    'record_MPI':False,
    # id of region simulate by nest
    'id_region_nest':[],
    # time of synchronization between node
    'synchronization':0.,#Todo compute with the min of delay
    # save step
    'save_step':0.,
    # percentage of shared rate between neurons of the same region
    'percentage_shared':0.5,
    # level of log : debug 0, info 1, warning 2, error 3, critical 4
    'level_log':1
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
    'g':3.5,
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
    'rate_ex':400*1e-3+2.0*150,
    'rate_in':200.0*1.e-3+0.0*150,
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
    'P_e':[-0.05059317,  0.0036078 ,  0.01794401,  0.00467008,  0.00098553,  0.0082953 , -0.00985289, -0.02600252, -0.00274499, -0.01051463],
    # 'P_e':[-0.04994512,  0.00033889,  0.00434596,  0.00122126,  0.00584339, -0.00048078, -0.0001464,   0.00140099, -0.00025785, -0.00141249],
    'P_e':[-0.0506587 ,  0.0026406 , -0.00151409, -0.00810736,  0.00081096,   0.01194696, -0.00728937,  0.00156232,  0.00462174, -0.00576466],
    # Polynome for inhibitory neurons | WARNING: should be change when the parameter of neurons change)
    # 'P_i':[-0.05084858,  0.00146866, -0.00657981,  0.0014993 , -0.0003816 ,  0.00020026,  0.00078719, -0.00322428, -0.00842626, -0.0012793 ],
    # 'P_i':[-0.04959247, -0.00113669,  0.00093422, -0.00560576,  0.00292606, -0.02052566,  0.0105556,  -0.00163008,  0.00447567, -0.00182161],
    'P_i':[-5.96722865e-02,  7.15675508e-03,  4.28252163e-03,  9.25089702e-03,  1.16632197e-06, -1.00659310e-02,  3.89257235e-03,  4.45787751e-04,  4.20050937e-03,  4.37359879e-03],

    # initial condition, should be simmilar than nest #TODO
    'initial_condition':{"E": [0.0, 0.0], "I": [0.0, 0.0], "C_ii": [0.0, 0.0], "W_e": [0.0, 0.0], "C_ee": [0.0, 0.0], "C_ei": [0.0, 0.0], "W_i": [0.0, 0.0]},
}

param_TR_nest_to_tvb={
    # 'init': path of the initialisation of the translation if not the run exploration will create it
    # 'resolution': param_nest['sim_resolution']
    # 'synch': param_co_simulation['synchronization']
    # 'width': param_zerlaut['T']
    # 'level_log': param_co_simulation['level_log']
}

param_TR_tvb_to_nest={
    # 'init': path of the initialisation of the translation if not the run exploration will create it
}
