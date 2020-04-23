import datetime
import os
import nest
from nest_elephant_tvb.simulation.simulation_nest import simulate,config_mpi_record,simulate_mpi_co_simulation
from nest_elephant_tvb.simulation.simulation_zerlaut import simulate_tvb
import subprocess
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
    if parameter_default.param_co_simulation['co-simulation']:
        if not hasattr(param_TR_tvb_to_nest, 'init'):
            path_rates = results_path+'/init_rates.npy'
            init_rates = np.array([[] for i in range(param_topology['nb_neuron_by_region'])])
            np.save(path_rates,init_rates)
            param_TR_tvb_to_nest['init']= path_rates

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
           param_TR_tvb_to_nest,param_TR_nest_to_tvb


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


def run(results_path,parameter_default,dict_variable,begin,end):
    """
    Run one simulation, analyse the simulation and save this result in the database
    :param results_path: the folder where to save spikes
    :param parameter_default: parameters by default of the exploration
    :param dict_variable : dictionary with the variable change
    :param begin:  when start the recording simulation ( not take in count for tvb (start always to zeros )
    :param end: when end the recording simulation and the simulation
    :return: nothing
    """
    print('time: '+str(datetime.datetime.now())+' BEGIN SIMULATION \n')
    #create the folder for result is not exist
    newpath = os.path.join(os.getcwd(),results_path)
    # start to create the repertory for the simulation
    if nest.Rank() == 0:
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        if not os.path.exists(newpath+"/log"):
            os.makedirs(newpath+"/log")
        if not os.path.exists(newpath + '/tvb'):
            os.makedirs(newpath + '/tvb')
        else:
            try:
                os.remove(newpath + '/tvb/step_init.npy') # use it for synchronise all mpi the beginning
            except OSError:
                pass
    else:
        while not os.path.exists(newpath+'/tvb'): # use it for synchronise all nest thread
            pass

    # generate parameter for the  simulation
    param_nest,param_topology,param_connection,\
    param_background,param_tvb,param_zerlaut,\
    param_TR_tvb_to_nest,param_TR_nest_to_tvb\
        = generate_parameter(parameter_default,results_path,dict_variable)

    # parameter for the cosimulation and more
    param_co_simulation = parameter_default.param_co_simulation

    save_parameter(param_co_simulation,param_tvb,param_zerlaut,param_nest,param_topology,param_connection,
                   param_background,param_TR_tvb_to_nest,param_TR_nest_to_tvb,
                   results_path,begin,end)

    if param_co_simulation['co-simulation']:
        # First case : co-simulation
        id_proxy =  param_co_simulation['id_region_nest']
        time_synch =  param_co_simulation['synchronization']

        #initialise Nest and take information for the connection between all the mpi process
        spike_detector,spike_generator = config_mpi_record(results_path=results_path,begin=begin,end=end,
                param_nest=param_nest,param_topology=param_topology,
                param_connection=param_connection,param_background=param_background,
                                                           cosimulation=param_co_simulation)
        if nest.Rank() == 0:
            # create translator between Nest to TVB :
            # one by proxy/spikedetector

            # create all the repertory for the translation file (communication files of MPI)
            if not os.path.exists(newpath+"/spike_detector/"):
                        os.makedirs(newpath+"/spike_detector/")
            if not os.path.exists(newpath+"/send_to_tvb/"):
                os.makedirs(newpath+"/send_to_tvb/")


            for index,id_spike_detector in enumerate(spike_detector):
                dir_path = os.path.dirname(os.path.realpath(__file__))+"/file_translation/run_mpi_nest_to_tvb.sh"
                argv=[ dir_path,
                       results_path,
                       "/spike_detector/"+str(id_spike_detector.tolist()[0])+".txt",
                       "/send_to_tvb/"+str(id_proxy[index])+".txt",
                       ]
                subprocess.Popen(argv,
                                 #need to check if it's needed or not (doesn't work for me)
                                 stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                                 )

            # create translator between TVB to Nest:
            # one by proxy/id_region

            # create all the repertory for the translation file (communication files of MPI)
            if not os.path.exists(results_path+"/spike_generator/"):
                os.makedirs(newpath+"/spike_generator/")
            if not os.path.exists(results_path+"/receive_from_tvb/"):
                os.makedirs(newpath+"/receive_from_tvb/")

            for index,ids_spike_generator in enumerate(spike_generator):
                dir_path = os.path.dirname(os.path.realpath(__file__))+"/file_translation/run_mpi_tvb_to_nest.sh"
                argv=[ dir_path,
                       results_path+"/spike_generator/",
                       str(ids_spike_generator.tolist()[0]),
                       str(len(ids_spike_generator.tolist())),
                       "/../receive_from_tvb/"+str(id_proxy[index])+".txt",
                       str(param_co_simulation['percentage_shared']),
                       str(param_co_simulation['level_log'])
                       ]
                subprocess.Popen(argv,
                                 #need to check if it's needed or not (doesn't work for me)
                                 stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                                 )
            #TODO correct synchronization : waiting until create most all file of config

            # Run TVB in co-simulation
            dir_path = os.path.dirname(os.path.realpath(__file__))+"/file_tvb/run_mpi_tvb.sh"
            argv=[
                dir_path,
                results_path
            ]
            subprocess.Popen(argv,
                             # need to check if it's needed or not (doesn't work for me)
                             stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                             )
        # Use the init file of TVB for waiting the configuration file for MPI communication are ready to use
        # and start the simulation at the same time
        while not os.path.exists(newpath+'/tvb/step_init.npy'):
             pass
        simulate_mpi_co_simulation(time_synch,end,newpath,param_co_simulation['level_log'])

    else:
        if param_co_simulation['nb_MPI_nest'] != 0:
            # Second case : Only nest simulation
            if param_co_simulation['record_MPI']:
                time_synch =  param_co_simulation['synchronization']
                #initialise Nest before the communication
                spike_detector,spike_generator = config_mpi_record(results_path=results_path,begin=begin,end=end,
                param_nest=param_nest,param_topology=param_topology,
                param_connection=param_connection,param_background=param_background,
                cosimulation = param_co_simulation)

                #create file for the foldder for the communication part
                if nest.Rank() == 0:
                    if not os.path.exists(results_path+'/spike_detector/'):
                        os.makedirs(results_path+'/spike_detector/')
                    if not os.path.exists(results_path + '/save/'):
                        os.makedirs(results_path + '/save/')
                else:
                    while not os.path.exists(results_path+'/save/'):
                        pass

                #TODO need to test and to finish this part
                for index,id_spike_detector in enumerate(spike_detector):
                    dir_path = os.path.dirname(os.path.realpath(__file__))+"/file_translation/run_mpi_nest_save.sh"
                    argv=[ dir_path,
                           results_path,
                           "/spike_detector/"+str(id_spike_detector.tolist()[0])+".txt",
                           results_path+"/save/"+str(id_spike_detector.tolist()[0]),
                           str(param_nest['sim_resolution']),
                           str(time_synch),
                           str(np.ceil(end/time_synch)),
                           str(param_co_simulation['save_step']),
                           str(param_co_simulation['level_log']),
                           ]
                    subprocess.Popen(argv,
                                 #need to check if it's needed or not (doesn't work for me)
                                 stdin=None,stdout=None,stderr=None,close_fds=True, #close the link with parent process
                                 )
                simulate_mpi_co_simulation(time_synch, end, newpath, param_co_simulation['level_log'])
            else:
                # just run nest with the configuration
                simulate(results_path=results_path, begin=begin, end=end,
                     param_nest=param_nest, param_topology=param_topology,
                     param_connection=param_connection, param_background=param_background)
        else:
            # Third case : Only tvb simulation
            simulate_tvb(results_path=results_path,begin=begin,end=end,
                param_tvb=param_tvb,param_zerlaut=param_zerlaut,
                param_nest=param_nest,param_topology=param_topology,
                param_connection=param_connection,param_background=param_background)
    print('time: '+str(datetime.datetime.now())+' END SIMULATION \n')

def run_exploration_2D(path,parameter_default,dict_variables,begin,end):
    """

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
            run(results_path,parameter_default,{name_variable_1:variable_1,name_variable_2:variable_2},begin,end)
            # except:
            #     sys.stderr.write('time: '+str(datetime.datetime.now())+' error: ERROR in simulation \n')
