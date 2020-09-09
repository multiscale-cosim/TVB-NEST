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
from nest_elephant_tvb.orchestrator.parameters_manager import generate_parameter,save_parameter

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
    if param_co_simulation['cluster']:
        mpirun = 'srun'
    else:
        mpirun = 'mpirun'

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
        dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../Tvb/run_mpi_tvb.sh"
        argv = [
            '/bin/sh',
            dir_path,
            mpirun,
            str(1),
            results_path,
        ]
        processes.append(subprocess.Popen(argv,
                         # need to check if it's needed or not (doesn't work for me)
                         stdin=None, stdout=None, stderr=None, close_fds=True,  # close the link with parent process
                         ))

        # create translator between Nest to TVB :
        # one by proxy/spikedetector
        for index,id_spike_detector in enumerate(spike_detector):
            dir_path = os.path.dirname(os.path.realpath(__file__))+"/../translation/run_mpi_nest_to_tvb.sh"
            argv=[ '/bin/sh',
                   dir_path,
                   mpirun,
                   results_path,
                   "/translation/spike_detector/"+str(id_spike_detector)+".txt",
                   "/translation/send_to_tvb/"+str(id_proxy[index])+".txt",
                   ]
            processes.append(subprocess.Popen(argv,
                             #need to check if it's needed or not (doesn't work for me)
                             stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                             ))

        # create translator between TVB to Nest:
        # one by proxy/id_region
        for index,ids_spike_generator in enumerate(spike_generator):
            dir_path = os.path.dirname(os.path.realpath(__file__))+"/../translation/run_mpi_tvb_to_nest.sh"
            argv=[ '/bin/sh',
                   dir_path,
                   mpirun,
                   results_path+"/translation/spike_generator/",
                   str(ids_spike_generator[0]),
                   str(len(ids_spike_generator)),
                   "/../receive_from_tvb/"+str(id_proxy[index])+".txt",
                   ]
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

if __name__ == "__main__":
    if len(sys.argv)==2:
        run(parameters_file=sys.argv[1])
    else:
        print('missing argument')
