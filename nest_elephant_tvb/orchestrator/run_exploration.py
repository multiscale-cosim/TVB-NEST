#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import datetime
import os
import sys
import json
import subprocess
import logging
import time
import numpy as np

def run(parameters_file):
    '''
    run the simulation
    :param parameters_file: parameters of the simulation
    :return:
    '''
    with open(parameters_file) as f:
        parameters = json.load(f)

    #create the folder for result is not exist
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
    logger = logging.getLogger('orchestrator')
    fh = logging.FileHandler(results_path + '/log/orchestrator.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if level_log == 0:
        fh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif  level_log == 1:
        fh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif  level_log == 2:
        fh.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    elif  level_log == 3:
        fh.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    elif  level_log == 4:
        fh.setLevel(logging.CRITICAL)
        logger.setLevel(logging.CRITICAL)

    logger.info('time: '+str(datetime.datetime.now())+' BEGIN SIMULATION \n')

    # chose between running on cluster or local pc
    mpirun = param_co_simulation['mpi'] # example : ['mpirun'] , ['srun','-N','1']

    processes = [] # process generate for the co-simulation
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

        id_proxy = param_co_simulation['id_region_nest']

        #Run Nest and take information for the connection between all the mpi process
        if 'singularity' in param_co_simulation.keys() :
            argv = mpirun+['-n',str(param_co_simulation['nb_MPI_nest']),'singularity','run', '--app', 'nest',param_co_simulation['singularity'] ]
        elif 'sarus' in param_co_simulation.keys():
            argv = mpirun + ['-n', str(param_co_simulation['nb_MPI_nest'])] + param_co_simulation['sarus'] + [
                'python3', 'home/nest_elephant_tvb/Nest/simulation_Zerlaut.py']
        elif 'docker' in param_co_simulation.keys():
            argv = param_co_simulation['docker']+mpirun+['-n',str(param_co_simulation['nb_MPI_nest'])]+['python3','home/nest_elephant_tvb/Nest/simulation_Zerlaut.py']
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__))+"/../Nest/run_mpi_nest.sh"
            argv=[
                '/bin/sh',
                dir_path,
                mpirun[0],
                str(param_co_simulation['nb_MPI_nest']),
            ]
        argv+= [
            str(1),
            results_path,
        ]
        print(argv);sys.stdout.flush()
        processes.append(subprocess.Popen(argv,
                 # need to check if it's needed or not (doesn't work for me)
                 stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                 ))
        while not os.path.exists(results_path+'/nest/spike_generator.txt.unlock'):
            logger.info("spike generator ids not found yet, retry in 1 second")
            time.sleep(1)
        os.remove(results_path+'/nest/spike_generator.txt.unlock')
        spike_generator = np.loadtxt(results_path+'/nest/spike_generator.txt',dtype=int)
        while not os.path.exists(results_path+'/nest/spike_detector.txt.unlock'):
            logger.info("spike detector ids not found yet, retry in 1 second")
            time.sleep(1)
        os.remove(results_path+'/nest/spike_detector.txt.unlock')
        spike_detector = np.loadtxt(results_path+'/nest/spike_detector.txt',dtype=int)
        # case of one spike detector
        try :
            spike_detector = np.array([int(spike_detector)])
            spike_generator = np.expand_dims(spike_generator,0)
        except:
            pass

        # print ids of nest population
        print("Ids of different populations of Nest :\n")
        f = open(results_path+'/nest/population_GIDs.dat', 'r')
        print(f.read())
        f.close()

        # Run TVB in co-simulation
        if 'singularity' in param_co_simulation.keys()  :
            argv = mpirun + ['-n','1','singularity','run', '--app', 'TVB',param_co_simulation['singularity']]
        elif 'sarus' in param_co_simulation.keys():
            argv = mpirun + ['-n', '1'] + param_co_simulation['sarus'] + ['python3', 'home/nest_elephant_tvb/Tvb/simulation_Zerlaut.py']
        elif 'docker' in param_co_simulation.keys():
            argv =  param_co_simulation['docker']+mpirun + ['-n','1'] +['python3','home/nest_elephant_tvb/Tvb/simulation_Zerlaut.py']
        else:
            dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../Tvb/run_mpi_tvb.sh"
            argv = [
                '/bin/sh',
                dir_path,
                mpirun[0],
            ]
        argv+= [
            str(1),
            results_path,
        ]
        print(argv);sys.stdout.flush()
        processes.append(subprocess.Popen(argv,
                         # need to check if it's needed or not (doesn't work for me)
                         stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                         ))

        # create translator between Nest to TVB :
        # one by proxy/spikedetector
        for index,id_spike_detector in enumerate(spike_detector):
            if 'singularity' in param_co_simulation.keys() :
                argv = mpirun+[ '-n','3','singularity', 'run', '--app', 'NEST-TVB',param_co_simulation['singularity']]
            elif 'docker' in param_co_simulation.keys():
                argv = param_co_simulation['docker'] + mpirun + ['-n', '3'] + ['python3','home/nest_elephant_tvb/translation/nest_to_tvb.py']
            elif 'sarus' in param_co_simulation.keys():
                argv = mpirun + ['-n','3'] + param_co_simulation['sarus']+['python3','home/nest_elephant_tvb/translation/nest_to_tvb.py']
            else:
                dir_path = os.path.dirname(os.path.realpath(__file__))+"/../translation/run_mpi_nest_to_tvb.sh"
                argv=[ '/bin/sh',
                   dir_path,
                   mpirun[0]]
            argv+= [
                   results_path,
                   "/translation/spike_detector/"+str(id_spike_detector)+".txt",
                   "/translation/send_to_tvb/"+str(id_proxy[index])+".txt",
                   ]
            print(argv);sys.stdout.flush()
            processes.append(subprocess.Popen(argv,
                             #need to check if it's needed or not (doesn't work for me)
                             stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                             ))

        # create translator between TVB to Nest:
        # one by proxy/id_region
        for index,ids_spike_generator in enumerate(spike_generator):
            if 'singularity' in param_co_simulation.keys() :
                argv = mpirun+['-n','3','singularity', 'run', '--app', 'TVB-NEST',param_co_simulation['singularity']]
            elif 'sarus' in param_co_simulation.keys():
                argv = mpirun + ['-n','3'] + param_co_simulation['sarus'] +['python3','home/nest_elephant_tvb/translation/tvb_to_nest.py']
            elif 'docker' in param_co_simulation.keys():
                argv = param_co_simulation['docker'] + mpirun + ['-n', '3'] + ['python3','home/nest_elephant_tvb/translation/tvb_to_nest.py']
            else:
                dir_path = os.path.dirname(os.path.realpath(__file__))+"/../translation/run_mpi_tvb_to_nest.sh"
                argv=[ '/bin/sh',
                   dir_path,
                   mpirun[0]]
            argv+= [
                   results_path+"/translation/spike_generator/",
                   str(ids_spike_generator[0]),
                   str(len(ids_spike_generator)),
                   "/../receive_from_tvb/"+str(id_proxy[index])+".txt",
                   ]
            print(argv);sys.stdout.flush()
            processes.append(subprocess.Popen(argv,
                             #need to check if it's needed or not (doesn't work for me)
                             stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                             ))
    else:
        if param_co_simulation['nb_MPI_nest'] != 0:
            # Second case : Only nest simulation
            if param_co_simulation['record_MPI']:
                # translator for saving some result
                if not os.path.exists(results_path + '/translation'):
                    os.makedirs(results_path + '/translation')
                end = parameters['end']

                #initialise Nest before the communication
                dir_path = os.path.dirname(os.path.realpath(__file__))+"/../Nest/run_mpi_nest.sh"
                argv=[
                    '/bin/sh',
                    dir_path,
                    mpirun,
                    str(param_co_simulation['nb_MPI_nest']),
                    str(1),
                    results_path,
                ]
                processes.append(subprocess.Popen(argv,
                         # need to check if it's needed or not (doesn't work for me)
                         stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                         ))
                while not os.path.exists(results_path+'/nest/spike_detector.txt.unlock'):
                    logger.info("spike detector ids not found yet, retry in 1 second")
                    time.sleep(1)
                os.remove(results_path+'/nest/spike_detector.txt.unlock')
                spike_detector = np.loadtxt(results_path+'/nest/spike_detector.txt',dtype=int)

                # Create folder for the translation part
                if not os.path.exists(results_path+'/translation/spike_detector/'):
                    os.makedirs(results_path+'/translation/spike_detector/')
                if not os.path.exists(results_path + '/translation/save/'):
                    os.makedirs(results_path + '/translation/save/')

                for id_spike_detector in spike_detector:
                    dir_path = os.path.dirname(os.path.realpath(__file__))+"/../translation/run_mpi_nest_save.sh"
                    argv=[ '/bin/sh',
                           dir_path,
                           mpirun,
                           results_path,
                           "/translation/spike_detector/"+str(id_spike_detector)+".txt",
                           results_path+"/translation/save/"+str(id_spike_detector),
                           str(end)
                           ]
                    processes.append(subprocess.Popen(argv,
                                 #need to check if it's needed or not (doesn't work for me)
                                 stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                                 ))
            else:
                #Run Nest with MPI
                dir_path = os.path.dirname(os.path.realpath(__file__))+"/../Nest/run_mpi_nest.sh"
                argv=[
                    '/bin/sh',
                    dir_path,
                    mpirun,
                    str(param_co_simulation['nb_MPI_nest']),
                    str(0),
                    results_path,
                ]
                processes.append(subprocess.Popen(argv,
                         # need to check if it's needed or not (doesn't work for me)
                         stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                         ))
        else:
            # TODO change the API for include Nest without MPI
            # Run TVB in co-simulation
            dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../Tvb/simulation_Zerlaut.py"
            argv = [
                'python3',
                dir_path,
                str(0),
                results_path,
            ]
            processes.append(subprocess.Popen(argv,
                             # need to check if it's needed or not (doesn't work for me)
                             stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                             ))
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
            os.remove(newpath + '/parameter.py') # use it for synchronise all mpi the beginning
        except OSError:
            pass
    # generate and save parameter for the  simulation
    parameters = generate_parameter(parameter_default,results_path,dict_variable)
    save_parameter(parameters,results_path,begin,end)
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
    name_variable_1,name_variable_2 = dict_variables.keys()
    print(path)
    for variable_1 in  dict_variables[name_variable_1]:
        for variable_2 in  dict_variables[name_variable_2]:
            # try:
            print('SIMULATION : '+name_variable_1+': '+str(variable_1)+' '+name_variable_2+': '+str(variable_2))
            results_path=path+'_'+name_variable_1+'_'+str(variable_1)+'_'+name_variable_2+'_'+str(variable_2)
            run_exploration(results_path,parameter_default,{name_variable_1:variable_1,name_variable_2:variable_2},begin,end)
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
