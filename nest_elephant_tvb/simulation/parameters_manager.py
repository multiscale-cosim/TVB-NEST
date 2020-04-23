import json
import numpy as np
import subprocess
import os

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
    param_nest = parameter_default.param_nest
    param_topology = parameter_default.param_topology
    param_connection = parameter_default.param_connection
    param_background = parameter_default.param_background
    param_tvb = parameter_default.param_tvb
    param_zerlaut = parameter_default.param_zerlaut
    param_TR_tvb_to_nest = parameter_default.param_TR_tvb_to_nest
    param_TR_nest_to_tvb = parameter_default.param_TR_nest_to_tvb
    if dict_variable != None:
        for variable in dict_variable.keys():
            if variable in param_nest.keys():
                param_nest[variable]=dict_variable[variable]
            elif variable in param_topology.keys():
                param_topology[variable]=dict_variable[variable]
            elif variable in param_topology['param_neuron_excitatory'].keys():
                param_topology['param_neuron_excitatory'][variable]=dict_variable[variable]
            #elif variable in param_topology['param_neuron_inhibitory'].keys():
            #   param_topology['param_neuron_inhibitory'][variable] = dict_variable[variable]
            elif variable in param_connection.keys():
                param_connection[variable]=dict_variable[variable]
            elif variable in param_background.keys():
                param_background[variable]=dict_variable[variable]
            elif variable in param_TR_nest_to_tvb:
                param_TR_nest_to_tvb[variable]=dict_variable[variable]
            elif variable in param_TR_tvb_to_nest:
                param_TR_tvb_to_nest[variable] = dict_variable[variable]

    return create_linked_parameters(results_path,parameter_default,param_nest,param_topology,param_connection,param_background,param_tvb,param_zerlaut, \
           param_TR_tvb_to_nest,param_TR_nest_to_tvb)


def create_linked_parameters(results_path,parameter_default,param_nest,param_topology,param_connection,param_background,param_tvb,param_zerlaut, \
           param_TR_tvb_to_nest,param_TR_nest_to_tvb):

    # parameters for the translation TVB to Nest
    if parameter_default.param_co_simulation['co-simulation']:
        if not hasattr(param_TR_tvb_to_nest, 'init'):
            path_rates = results_path+'/init_rates.npy'
            init_rates = np.array([[] for i in range(param_topology['nb_neuron_by_region'])])
            np.save(path_rates,init_rates)
            param_TR_tvb_to_nest['init']= path_rates
    param_TR_tvb_to_nest['level_log']= parameter_default.param_co_simulation['level_log']

    # parameters for the translation nest to TVB
    if not hasattr(param_TR_nest_to_tvb, 'init'):
        path_spikes = results_path+'/init_spikes.npy'
        init_spikes = np.zeros((int(parameter_default.param_co_simulation['synchronization']/param_nest['sim_resolution']),1))
        np.save(path_spikes,init_spikes)
        param_TR_nest_to_tvb['init']= path_spikes
    param_TR_nest_to_tvb['resolution']=param_nest['sim_resolution']
    param_TR_nest_to_tvb['synch']=parameter_default.param_co_simulation['synchronization']
    param_TR_nest_to_tvb['width']=param_zerlaut['T']
    param_TR_nest_to_tvb['level_log']= parameter_default.param_co_simulation['level_log']

    return param_nest,param_topology,param_connection,param_background,param_tvb,param_zerlaut,\
           param_TR_tvb_to_nest, param_TR_nest_to_tvb


def save_parameter(param_co_simulation,param_tvb,param_zerlaut,param_nest,param_topology,param_connection,
                   param_background,param_TR_tvb_to_nest,param_TR_nest_to_tvb,results_path,begin,end):
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
    f = open(results_path+'/parameter.py',"w")
    for name,dic in [('param_co_simulation',param_co_simulation),
                     ('param_tvb',param_tvb),
                     ('param_zerlaut',param_zerlaut),
                     ('param_nest',param_nest),
                     ('param_topology',param_topology),
                     ('param_connection',param_connection),
                     ('param_background',param_background),
                     ('param_TR_nest_to_tvb',param_TR_nest_to_tvb),
                     ('param_TR_tvb_to_nest', param_TR_tvb_to_nest),
                     ]:
        f.write(name+' = ')
        json.dump(dic, f)
        f.write("\n")
    f.write('result_path="'+results_path+"/\"\n")
    f.write("begin=" + str(begin) + "\n")
    f.write("end=" + str(end) + "\n")
    f.close()
    subprocess.call([os.path.dirname(os.path.abspath(__file__))+'/correct_parameter.sh',results_path+'/parameter.py']) ##Warning can be don't find the script

