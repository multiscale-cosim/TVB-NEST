#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import datetime
import os
import sys
import json
import subprocess
import time
import numpy as np
import copy
import logging


def create_logger(path, name, log_level):
    """
    creation of logger for module
    :param path: path of the logger
    :param name: name of the module
    :param log_level: level of logger
    :return:
    """
    # Configure logger
    logger = logging.getLogger(name)
    fh = logging.FileHandler(path+'/log/'+name+'.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if log_level == 0:
        fh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif  log_level == 1:
        fh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif  log_level == 2:
        fh.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    elif  log_level == 3:
        fh.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    elif  log_level == 4:
        fh.setLevel(logging.CRITICAL)
        logger.setLevel(logging.CRITICAL)

    return logger


def run(parameters_file):
    '''
    run the simulation
    :param parameters_file: parameters of the simulation
    :return:
    '''
    with open(parameters_file) as f:
        parameters = json.load(f)

    # create the folder for result is not exist
    results_path = os.path.join(os.getcwd(),parameters['result_path'])
    # start to create the repertory for the simulation
    if not os.path.exists(results_path):
        os.makedirs(results_path)
    if not os.path.exists(results_path+"/log"):
        os.makedirs(results_path+"/log")
    if not os.path.exists(results_path + '/nest'):
        os.makedirs(results_path + '/nest')
    if not os.path.exists(results_path + '/tvb'):
        os.makedirs(results_path + '/tvb')

    # parameter for the co-simulation
    param_co_simulation = parameters['param_co_simulation']

    # configuration of the logger
    level_log = param_co_simulation['level_log']
    logger = create_logger(results_path, 'orchestrator', level_log)

    logger.info('time: '+str(datetime.datetime.now())+' BEGIN SIMULATION \n')

    # chose between running on cluster or local pc
    mpirun = param_co_simulation['mpi']  # example : ['mpirun'] , ['srun','-N','1']

    # id of the region of nest of the brain
    id_proxy = param_co_simulation['id_region_nest']

    processes = []  # process generate for the co-simulation
    if param_co_simulation['co-simulation']:
        # First case : co-simulation
        if not os.path.exists(results_path + '/translation'):
            os.makedirs(results_path + '/translation')
        # create all the repertory for the translation file (communication files of MPI)
        if not os.path.exists(results_path+"/translation/spike_detector/"):
            os.makedirs(results_path+"/translation/spike_detector/")
        if not os.path.exists(results_path+"/translation/send_to_tvb/"):
            os.makedirs(results_path+"/translation/send_to_tvb/")
        # create all the repertory for the translation file (communication files of MPI)
        if not os.path.exists(results_path+"/translation/spike_generator/"):
            os.makedirs(results_path+"/translation/spike_generator/")
        if not os.path.exists(results_path+"/translation/receive_from_tvb/"):
            os.makedirs(results_path+"/translation/receive_from_tvb/")
        if parameters['param_TR_nest_to_tvb']['save_hist']:
            if not os.path.exists(results_path+'/translation/TSR_hist/'):
                os.mkdir(results_path+'/translation/TSR_hist/')
        if parameters['param_TR_nest_to_tvb']['save_rate']:
            if not os.path.exists(results_path+'/translation/TSR_rate/'):
                os.mkdir(results_path+'/translation/TSR_rate/')
        if parameters['param_TR_tvb_to_nest']['save_spike']:
            if not os.path.exists(results_path+'/translation/TRS_spike/'):
                os.mkdir(results_path+'/translation/TRS_spike/')
        if parameters['param_TR_tvb_to_nest']['save_rate']:
            if not os.path.exists(results_path+'/translation/TSR_rate/'):
                os.mkdir(results_path+'/translation/TSR_rate/')

        # Run Nest and take information for the connection between all the mpi process
        if 'singularity' in param_co_simulation.keys() :  # run with singularity image
            argv = mpirun+['-n', str(param_co_simulation['nb_MPI_nest']),'singularity','run',
                           '--app', 'nest', param_co_simulation['singularity']]
        elif 'sarus' in param_co_simulation.keys():  # run from sarus on a cluster
            argv = mpirun + ['-n', str(param_co_simulation['nb_MPI_nest'])] + param_co_simulation['sarus']\
                   + ['python3', 'home/nest_elephant_tvb/Nest/simulation_Zerlaut.py']
        elif 'docker' in param_co_simulation.keys():  # run with docker
            argv = param_co_simulation['docker']+mpirun+['-n',str(param_co_simulation['nb_MPI_nest'])]\
                   + ['python3','home/nest_elephant_tvb/Nest/simulation_Zerlaut.py']
        else:  # run local or with slurm
            dir_path = os.path.dirname(os.path.realpath(__file__))+"/../Nest/simulation_Zerlaut.py"
            argv = copy.copy(mpirun)
            argv += ['-n', str(param_co_simulation['nb_MPI_nest']), 'python3', dir_path]
        argv += [results_path]
        print("Nest start :", argv);sys.stdout.flush()
        processes.append(subprocess.Popen(argv,
                         # need to check if it's needed or not (doesn't work for me)
                         stdin=None, stdout=None, stderr=None, close_fds=True, # close the link with parent process
                         ))

        # create translator between Nest to TVB :
        # one by proxy/spikedetector
        nb_mpi_translator = 1 if param_co_simulation['translation_thread'] else 3
        for index in range(len(id_proxy)):
            if 'singularity' in param_co_simulation.keys():  # run with singularity image
                argv = mpirun+['-n', str(nb_mpi_translator),'singularity', 'run',
                               '--app', 'NEST-TVB', param_co_simulation['singularity']]
            elif 'docker' in param_co_simulation.keys():  # run from sarus on a cluster
                argv = param_co_simulation['docker'] + mpirun + ['-n', str(nb_mpi_translator)]\
                       + ['python3', 'home/nest_elephant_tvb/translation/nest_to_tvb.py']
            elif 'sarus' in param_co_simulation.keys():  # run with docker
                argv = mpirun + ['-n', str(nb_mpi_translator)] + param_co_simulation['sarus']\
                       + ['python3', 'home/nest_elephant_tvb/translation/nest_to_tvb.py']
            else:  # run local or with slurm
                dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../translation/nest_to_tvb.py"
                argv = copy.copy(mpirun)
                argv += ['-n', str(nb_mpi_translator), 'python3', dir_path]
            argv += [results_path, str(index)]
            print("Translator nest to tvb start : ", argv);sys.stdout.flush()
            processes.append(subprocess.Popen(argv,
                             #need to check if it's needed or not (doesn't work for me)
                             stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                             ))

        # create translator between TVB to Nest:
        # one by proxy/id_region
        for index in range(len(id_proxy)):
            if 'singularity' in param_co_simulation.keys() :  # run with singularity image
                argv = mpirun+['-n', str(nb_mpi_translator), 'singularity', 'run',
                               '--app', 'TVB-NEST', param_co_simulation['singularity']]
            elif 'sarus' in param_co_simulation.keys():  # run from sarus on a cluster
                argv = mpirun + ['-n',str(nb_mpi_translator)] + param_co_simulation['sarus']\
                       + ['python3', 'home/nest_elephant_tvb/translation/tvb_to_nest.py']
            elif 'docker' in param_co_simulation.keys():  # run with docker
                argv = param_co_simulation['docker'] + mpirun + ['-n', str(nb_mpi_translator)]\
                       + ['python3', 'home/nest_elephant_tvb/translation/tvb_to_nest.py']
            else:  # run local or with slurm
                dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../translation/tvb_to_nest.py"
                argv = copy.copy(mpirun)
                argv += ['-n', str(nb_mpi_translator), 'python3',  dir_path]
            argv += [results_path, str(index)]
            processes.append(subprocess.Popen(argv,
                             #need to check if it's needed or not (doesn't work for me)
                             stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                             ))
            print("Translator tvb to nest start : ", argv);sys.stdout.flush()

        # Run TVB in co-simulation
        if 'singularity' in param_co_simulation.keys():  # run with singularity image
            argv = mpirun + ['-n', '1', 'singularity', 'run', '--app', 'TVB', param_co_simulation['singularity']]
        elif 'sarus' in param_co_simulation.keys():  # run from sarus on a cluster
            argv = mpirun + ['-n', '1'] + param_co_simulation['sarus']\
                   + ['python3', 'home/nest_elephant_tvb/Tvb/simulation_Zerlaut.py']
        elif 'docker' in param_co_simulation.keys():  # run with docker
            argv = param_co_simulation['docker'] + mpirun + ['-n', '1']\
                   + ['python3', 'home/nest_elephant_tvb/Tvb/simulation_Zerlaut.py']
        else:  # run local or with slurm
            dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../Tvb/simulation_Zerlaut.py"
            argv = copy.copy(mpirun)
            argv += ['-n', '1', "python3", dir_path]
        argv += [results_path]
        print("TVB start : ", argv); sys.stdout.flush()
        processes.append(subprocess.Popen(argv,
                                          # need to check if it's needed or not (doesn't work for me)
                                          stdin=None, stdout=None, stderr=None, close_fds=True,
                                          # close the link with parent process
                                          ))
    else:
        raise Exception('not implemented see the main project')

    # FAT END POINT : add monitoring of the different process
    for process in processes:
        process.wait()
    logger.info('time: '+str(datetime.datetime.now())+' END SIMULATION \n')

def run_exploration(results_path,parameter_default,dict_variable,begin,end):
    """
    Run one simulation of the exploration
    :param results_path: the folder where to save spikes
    :param parameter_default: parameters by default of the exploration
    :param dict_variable : dictionary with the variable change
    :param begin:  when start the recording simulation ( not take in count for tvb (start always to zeros )
    :param end: when end the recording simulation and the simulation
    :return: nothing
    """
    #create the folder for result is not exist
    newpath = os.path.join(os.getcwd(),results_path)
    # start to create the repertory for the simulation
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    else:
        try:
            os.remove(newpath + '/parameter.py')  # use it for synchronise all mpi the beginning
        except OSError:
            pass
    # generate and save parameter for the  simulation
    parameters = generate_parameter(parameter_default, results_path, dict_variable)
    save_parameter(parameters, results_path, begin, end)
    # check if the file is available
    while not os.path.exists(results_path + '/parameter.json'):
        time.sleep(1)
    run(results_path+'/parameter.json')


def run_exploration_2D(path,parameter_default,dict_variables,begin,end):
    """
    Run exploration of parameter in 2 dimensions
    :param path: for the result of the simulations
    :param parameter_default: the parameters by defaults of the simulations
    :param dict_variables: the variables and there range of value for the simulations
    :param begin: when start the recording simulation ( not take in count for tvb (start always to zeros )
    :param end: when end the recording simulation and the simulation
    :return:
    """
    name_variable_1, name_variable_2 = dict_variables.keys()
    print(path)
    for variable_1 in dict_variables[name_variable_1]:
        for variable_2 in dict_variables[name_variable_2]:
            # try:
            print('SIMULATION : '+name_variable_1+': '+str(variable_1)+' '+name_variable_2+': '+str(variable_2))
            results_path=path+'_'+name_variable_1+'_'+str(variable_1)+'_'+name_variable_2+'_'+str(variable_2)
            run_exploration(results_path, parameter_default, {name_variable_1: variable_1, name_variable_2: variable_2},
                            begin, end)
            # except:
            #     sys.stderr.write('time: '+str(datetime.datetime.now())+' error: ERROR in simulation \n')


def generate_parameter(parameter_default,results_path,dict_variable=None):
    """
    generate the  parameter for the actual simulation
    use for changing parameter for the exploration
    WARNING: not all parameters can be use for exploration, changing this function for add new parameters
             only  parameters of excitatory neurons can be changing
    :param parameter_default: parameters by default of the exploration
    :param results_path : the folder of the result
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
            #elif variable in parameters['param_topology']['param_neuron_inhibitory'].keys(): # TODO problem to difference between inihibitory and excitatory parameters
            #   parameters['param_topology']['param_neuron_inhibitory'][variable] = dict_variable[variable]
    return create_linked_parameters(results_path,parameters)


def create_linked_parameters(results_path,parameters):
    """
    Change the parameters following the link between them

    :param results_path: the folder to save the result
    :param parameters: dictionary of parameters
    :return: dictionary of parameters for the simulation
    """
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
    param_tvb_connection['velocity'] =  param_nest_connection['velocity']
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
    param_tvb_model['p_connect_e']=param_nest_connection['p_connect']
    param_tvb_model['p_connect_i']=param_nest_connection['p_connect']
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
        param_TR_tvb_to_nest['level_log']= param_co_simulation['level_log']
        param_TR_tvb_to_nest['seed'] = param_nest['master_seed']-3
        param_TR_tvb_to_nest['nb_synapses'] = param_nest_connection['nb_external_synapse']
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
        param_TR_nest_to_tvb['nb_neurons']=param_nest_topology['nb_neuron_by_region'] * (1-param_nest_topology['percentage_inhibitory'])
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
    save the parameters of the simulations in json file
    :param parameters: dictionary of parameters
    :param results_path: where to save the result
    :param begin: when start the recording simulation ( not take in count for tvb (start always to zeros )
    :param end:  when end the recording simulation and the simulation
    :return: nothing
    """
    # save the value of all parameters
    f = open(results_path+'/parameter.json',"wt")
    f.write("{\n")
    for param_name,param_dic in parameters.items():
        f.write('"'+param_name+'" : ')
        json.dump(param_dic, f)
        f.write(",\n")
    f.write('"result_path":"'+os.path.abspath(results_path)+"/\",\n")
    f.write('"begin":' + str(begin) + ",\n")
    f.write('"end":' + str(end) + "\n")
    f.write("}")
    f.close()


if __name__ == "__main__":
    if len(sys.argv)==2:
        run(parameters_file=sys.argv[1])
    else:
        print('missing argument')
