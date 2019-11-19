import datetime
import os
import nest
from simulation_nest import simulate,config_mpi_record,simulate_mpi_record
from simulation_zerlaut import simulate_tvb
import subprocess
import numpy as np

def generate_parameter(parameter_default,dict_variable=None):
    param_nest = parameter_default.param_nest
    param_topology = parameter_default.param_topology
    param_connection = parameter_default.param_connection
    param_background = parameter_default.param_background
    param_tvb = parameter_default.param_tvb
    param_zerlaut = parameter_default.param_zerlaut
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
    return param_nest,param_topology,param_connection,param_background,param_tvb,param_zerlaut

def run(results_path,parameter_default,dict_variable,begin,end):
    """
    Run one simulation, analyse the simulation and save this result in the database
    :param results_path: the folder where to save spikes
    :param data_base: the file of the database
    :param table_name: the name of the table of the database
    :param dict_variable : dictionnary with the variable change
    :param begin: the beginning of record spike
    :param end: the end of the simulation
    :param print_volt: print the voltage of the membrane of population
    :return: nothing
    """
    print('time: '+str(datetime.datetime.now())+' BEGIN SIMULATION \n')
    #create the folder for result is not exist
    newpath = os.path.join(os.getcwd(),results_path)
    if nest.Rank() == 0:
    	if not os.path.exists(newpath):
            os.makedirs(newpath)
        if not os.path.exists(newpath+'/tvb'):
            os.makedirs(newpath+'/tvb')
    else:
	    while not os.path.exists(newpath+'/tvb'):
		    pass

    param_nest,param_topology,param_connection,param_background,param_tvb,param_zerlaut = generate_parameter(parameter_default,dict_variable)

    param_co_simulation = parameter_default.param_co_simulation

    if param_co_simulation['co-simulation']:
        pass
    else:
        if param_co_simulation['nb_MPI_nest'] != 0:
            if param_co_simulation['record_MPI']:
                spike_detector = config_mpi_record(results_path=results_path,begin=begin,end=end,
                param_nest=param_nest,param_topology=param_topology,
                param_connection=param_connection,param_background=param_background)

                if nest.Rank() == 0:
                    if not os.path.exists(results_path+'/config_mpi_spike_detector/'):
                        os.makedirs(newpath+'/config_mpi_spike_detector')
                else:
                    while not os.path.exists(results_path+'/config_mpi_spike_detector/'):
                        pass

                dir_path = os.path.dirname(os.path.realpath(__file__))+"/file_translation/run_mpi_record_region_activity.sh"
                for i in spike_detector:
                    print(dir_path+" " +results_path+'/config_mpi_spike_detector/' +" "+str(i[0]))
                    subprocess.call(["bash",dir_path, results_path+'/config_mpi_spike_detector/',str(i[0])])
                simulate_mpi_record(end)
            else:
                simulate(results_path=results_path, begin=begin, end=end,
                     param_nest=param_nest, param_topology=param_topology,
                     param_connection=param_connection, param_background=param_background)
        else:
            simulate_tvb(results_path=results_path,begin=begin,end=end,
                param_tvb=param_tvb,param_zerlaut=param_zerlaut,
                param_nest=param_nest,param_topology=param_topology,
                param_connection=param_connection,param_background=param_background)
    print('time: '+str(datetime.datetime.now())+' END SIMULATION \n')

def run_exploration_2D(path,parameter_default,dict_variables,begin,end):
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
