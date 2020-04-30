import json
import numpy as np

def generate_parameter(parameter_default,results_path,dict_variable=None):
    """
    generate the  parameter for the actual simulation
    use for changing parameter for the exploration
    WARNING: not all parameters can be use for exploration, changing this function for add new paramters
             only  parameters of excitatory neurons can be changing
    :param parameter_default: parameters by default of the exploration
    :param dict_variable: the variable to change and there values
    :return:
    """
    # change the exploring parameter
    parameters = {}
    if dict_variable != None:
        for variable in dict_variable.keys():
            for parameters_name in dir(parameter_default):
                if 'param' in parameters_name:
                    parameters_values = getattr(parameter_default,parameters_name)
                    if variable in parameters_values:
                        parameters_values[variable]=dict_variable[variable]
                    parameters[parameters_name] = parameters_values
            if variable in parameters['param_nest_topology']['param_neuron_excitatory'].keys():
                parameters['param_nest_topology']['param_neuron_excitatory'][variable]=dict_variable[variable]
            #elif variable in parameters['param_topology']['param_neuron_inhibitory'].keys():
            #   parameters['param_topology']['param_neuron_inhibitory'][variable] = dict_variable[variable]
    return create_linked_parameters(results_path,parameters)


def create_linked_parameters(results_path,parameters):
    param_co_simulation = parameters['param_co_simulation']
    param_nest = parameters['param_nest']
    param_nest_connection = parameters['param_nest_connection']
    param_nest_topology = parameters['param_nest_topology']
    param_tvb_model = parameters['param_tvb_model']

    # link between parameter in nest :
    param_nest_background = parameters['param_nest_background']
    param_nest_background['weight_poisson'] = param_nest_connection['weight_local']
    parameters['param_nest_background'] = param_nest_background

    # link between parameter of TVB and parameter of NEST :

    ## connection
    param_tvb_connection = parameters['param_tvb_connection']
    param_tvb_connection['path_distance'] =  param_nest_connection['path_distance']
    param_tvb_connection['path_weight'] =  param_nest_connection['path_weight']
    param_tvb_connection['nb_region'] =  param_nest_topology['nb_region']
    parameters['param_tvb_connection'] = param_tvb_connection

    ## coupling
    param_tvb_coupling = parameters['param_tvb_coupling']
    param_tvb_coupling['a'] = param_nest_connection['weight_global']
    parameters['param_tvb_coupling'] = param_tvb_coupling

    ## integrator and noise
    param_tvb_integrator = parameters['param_tvb_integrator']
    param_tvb_integrator['sim_resolution'] = param_nest['sim_resolution']
    param_tvb_integrator['seed'] = param_nest['master_seed']-1
    param_tvb_integrator['seed_init'] = param_nest['master_seed']-2
    parameters['param_tvb_integrator'] = param_tvb_integrator

    ## parameter of the model
    param_tvb_model['g_L']=param_nest_topology['param_neuron_excitatory']['g_L']
    param_tvb_model['E_L_e']=param_nest_topology['param_neuron_excitatory']['E_L']
    param_tvb_model['E_L_i']=param_nest_topology['param_neuron_inhibitory']['E_L']
    param_tvb_model['C_m']=param_nest_topology['param_neuron_excitatory']['C_m']
    param_tvb_model['b_e']=param_nest_topology['param_neuron_excitatory']['b']
    param_tvb_model['a_e']=param_nest_topology['param_neuron_excitatory']['a']
    param_tvb_model['b_i']=param_nest_topology['param_neuron_inhibitory']['b']
    param_tvb_model['a_i']=param_nest_topology['param_neuron_inhibitory']['a']
    param_tvb_model['tau_w_e']=param_nest_topology['param_neuron_excitatory']['tau_w']
    param_tvb_model['tau_w_i']=param_nest_topology['param_neuron_inhibitory']['tau_w']
    param_tvb_model['E_e']=param_nest_topology['param_neuron_excitatory']['E_ex']
    param_tvb_model['E_i']=param_nest_topology['param_neuron_excitatory']['E_in']
    param_tvb_model['Q_e']=param_nest_connection['weight_local']
    param_tvb_model['Q_i']=param_nest_connection['weight_local']*param_nest_connection['g']
    param_tvb_model['tau_e']=param_nest_topology['param_neuron_excitatory']['tau_syn_ex']
    param_tvb_model['tau_i']=param_nest_topology['param_neuron_excitatory']['tau_syn_in']
    param_tvb_model['N_tot']=param_nest_topology['nb_neuron_by_region']
    param_tvb_model['p_connect']=param_nest_connection['p_connect']
    param_tvb_model['g']=param_nest_topology['percentage_inhibitory']
    param_tvb_model['K_ext_e']=param_nest_connection['nb_external_synapse']
    parameters['param_tvb_model'] = param_tvb_model

    ## monitor
    param_tvb_monitor = parameters['param_tvb_monitor']
    param_tvb_monitor['parameter_TemporalAverage']['period'] = param_nest['sim_resolution']*10.0
    param_tvb_monitor['parameter_Bold']['period'] = param_nest['sim_resolution']*20000.0
    parameters['param_tvb_monitor'] = param_tvb_monitor

    # Parameter for the translators
    if param_co_simulation['co-simulation']:
        # parameters for the translation TVB to Nest
        if 'param_TR_tvb_to_nest' in parameters.keys():
            param_TR_tvb_to_nest = parameters['param_TR_tvb_to_nest']
        else:
            param_TR_tvb_to_nest = {}
        if not 'init' in param_TR_tvb_to_nest.keys():
            path_rates = results_path+'/init_rates.npy'
            init_rates = np.array([[] for i in range(param_nest_topology['nb_neuron_by_region'])])
            np.save(path_rates,init_rates)
            param_TR_tvb_to_nest['init']= path_rates
        param_TR_tvb_to_nest['level_log']= param_co_simulation['level_log']
        param_TR_tvb_to_nest['seed'] = param_nest['master_seed']-3
        parameters['param_TR_tvb_to_nest'] = param_TR_tvb_to_nest


        # parameters for the translation nest to TVB
        if 'param_TR_nest_to_tvb' in parameters.keys():
            param_TR_nest_to_tvb = parameters['param_TR_nest_to_tvb']
        else:
            param_TR_nest_to_tvb = {}
        if not 'init' in param_TR_nest_to_tvb.keys():
            path_spikes = results_path+'/init_spikes.npy'
            init_spikes = np.zeros((int(param_co_simulation['synchronization']/param_nest['sim_resolution']),1))
            np.save(path_spikes,init_spikes)
            param_TR_nest_to_tvb['init']= path_spikes
        param_TR_nest_to_tvb['resolution']=param_nest['sim_resolution']
        param_TR_nest_to_tvb['synch']=param_co_simulation['synchronization']
        param_TR_nest_to_tvb['width']=param_tvb_model['T']
        param_TR_nest_to_tvb['level_log']= param_co_simulation['level_log']
        parameters['param_TR_nest_to_tvb']= param_TR_nest_to_tvb

    if param_co_simulation['record_MPI']:
        if 'param_record_MPI' in parameters.keys():
            param_record_MPI = parameters['param_record_MPI']
        else:
            param_record_MPI = {}
        param_record_MPI['resolution']=param_nest['sim_resolution']
        param_record_MPI['synch']=param_co_simulation['synchronization']
        param_record_MPI['level_log']= param_co_simulation['level_log']
        parameters['param_record_MPI']= param_record_MPI

    return parameters


def save_parameter(parameters,results_path,begin,end):
    """
    save the parameters of the simulations in on file which can be imported by python
    :param param_co_simulation:parameter for the cosimulations and parameters of the simulations
    :param param_tvb: parameters for tvb (some parameters are parameters nest)
    :param param_zerlaut: parameters for model of tvb (some parameters are parameters topology)
    :param param_nest: parameters for nest engine
    :param param_topology: parameters for neurons in regions
    :param param_connection: parameters for connections inside and between regions
    :param param_background: parameters for noise and stimulations
    :param results_path: where to save the result
    :param begin: when start the recording simulation ( not take in count for tvb (start always to zeros )
    :param end:  when end the recording simulation and the simulation
    :return: nothing
    """
    f = open(results_path+'/parameter.py',"wt")
    for param_name,param_dic in parameters.items():
        f.write(param_name+' = ')
        json.dump(param_dic, f)
        f.write("\n")
    f.write('result_path="'+results_path+"/\"\n")
    f.write("begin=" + str(begin) + "\n")
    f.write("end=" + str(end) + "\n")
    f.close()
    fin = open(results_path+'/parameter.py',"rt")
    data = fin.read().replace('true','True').replace('false','False')
    fin.close()
    fout = open(results_path+'/parameter.py',"wt")
    fout.write(data)
    fout.close()

