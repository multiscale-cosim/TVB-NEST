import nest_elephant_tvb.simulation.file_tvb.Zerlaut as Zerlaut
import tvb.simulator.lab as lab
import numpy.random as rgn
import numpy as np
import nest_elephant_tvb.simulation.file_tvb.noise as my_noise
import json
import os
import subprocess
import sys

def init(param_tvb,param_zerlaut,param_nest,param_topology,param_connection,param_background):
    '''
    Initialise the simulator with parameter
    :param param_tvb : parameter for the simulator tvb
    :param param_zerlaut : parameter for the model
    :param param_nest : parameter for the simulator of tvb from nest parameter
    :param param_connection : parameter for the connection between neurons and regions
    :param param_topology : parameter for the neurons and the population
    :param param_background : parameter for the noise
    :return: the simulator initialize
    '''
    ## initialise the random generator
    rgn.seed(param_nest['master_seed']-1)

    ## Model
    if param_zerlaut['order'] == 1:
        model = Zerlaut.Zerlaut_adaptation_first_order(variables_of_interest='E I W_e W_i'.split())
    elif param_zerlaut['order'] == 2:
        model = Zerlaut.Zerlaut_adaptation_second_order(variables_of_interest='E I C_ee C_ei C_ii W_e W_i'.split())
    else:
        raise Exception('Bad order for the model')

    model.g_L=np.array(param_topology['param_neuron_excitatory']['g_L'])
    model.E_L_e=np.array(param_topology['param_neuron_excitatory']['E_L'])
    model.E_L_i=np.array(param_topology['param_neuron_inhibitory']['E_L'])
    model.C_m=np.array(param_topology['param_neuron_excitatory']['C_m'])
    model.b_e=np.array(param_topology['param_neuron_excitatory']['b'])
    model.a_e=np.array(param_topology['param_neuron_excitatory']['a'])
    model.b_i=np.array(param_topology['param_neuron_inhibitory']['b'])
    model.a_i=np.array(param_topology['param_neuron_inhibitory']['a'])
    model.tau_w_e=np.array(param_topology['param_neuron_excitatory']['tau_w'])
    model.tau_w_i=np.array(param_topology['param_neuron_inhibitory']['tau_w'])
    model.E_e=np.array(param_topology['param_neuron_excitatory']['E_ex'])
    model.E_i=np.array(param_topology['param_neuron_excitatory']['E_in'])
    model.Q_e=np.array(param_connection['weight_local'])
    model.Q_i=np.array(param_connection['weight_local']*param_connection['g'])
    model.tau_e=np.array(param_topology['param_neuron_excitatory']['tau_syn_ex'])
    model.tau_i=np.array(param_topology['param_neuron_excitatory']['tau_syn_in'])
    model.N_tot=np.array(param_topology['nb_neuron_by_region'])
    model.p_connect=np.array(param_connection['p_connect'])
    model.g=np.array(param_topology['percentage_inhibitory'])
    model.T=np.array(param_zerlaut['T'])
    model.P_e=np.array(param_zerlaut['P_e'])
    model.P_i=np.array(param_zerlaut['P_i'])
    model.K_ext_e=np.array(param_connection['nb_external_synapse'])
    model.K_ext_i=np.array(0)
    model.external_input_ex_ex=np.array(0.)
    model.external_input_ex_in=np.array(0.)
    model.external_input_in_ex=np.array(0.0)
    model.external_input_in_in=np.array(0.0)
    model.state_variable_range['E'] =np.array( param_zerlaut['initial_condition']['E'])
    model.state_variable_range['I'] =np.array( param_zerlaut['initial_condition']['I'])
    if param_zerlaut['order'] == 2:
        model.state_variable_range['C_ee'] = np.array(param_zerlaut['initial_condition']['C_ee'])
        model.state_variable_range['C_ei'] = np.array(param_zerlaut['initial_condition']['C_ei'])
        model.state_variable_range['C_ii'] = np.array(param_zerlaut['initial_condition']['C_ii'])
    model.state_variable_range['W_e'] = np.array(param_zerlaut['initial_condition']['W_e'])
    model.state_variable_range['W_i'] = np.array(param_zerlaut['initial_condition']['W_i'])

    ## Connection
    tract_lengths = np.load(param_connection['path_distance'])
    weights = np.load(param_connection['path_weight'])
    nb_region = int(param_topology['nb_region'])
    connection = lab.connectivity.Connectivity(number_of_regions=nb_region,
                                                   tract_lengths=tract_lengths[:nb_region,:nb_region],
                                                   weights=weights[:nb_region,:nb_region],
                                               region_labels=np.array([],dtype=np.dtype('<U128')),
                                               centres=np.array([])
                                               )

    ## Coupling
    coupling = lab.coupling.Linear(a=np.array(param_connection['weight_global']),
                                       b=np.array(0.0))

    ## Integrator
    noise = my_noise.Ornstein_Ulhenbeck_process(nsig=np.array(param_zerlaut['noise_parameter']['nsig']),
                                                    ntau=param_zerlaut['noise_parameter']['ntau'])
    noise.random_stream.seed(param_nest['master_seed']-1)
    integrator = lab.integrators.HeunStochastic(noise=noise,dt=param_nest['sim_resolution'])

    ## Monitors
    monitors =[]
    if param_tvb['Raw']:
        monitors.append(lab.monitors.Raw())
    if param_tvb['TemporalAverage']:
        monitor_TAVG = lab.monitors.TemporalAverage(
            variables_of_interest=param_tvb['parameter_TemporalAverage']['variables_of_interest'],
            period=param_tvb['parameter_TemporalAverage']['period'])
        monitors.append(monitor_TAVG)
    if param_tvb['Bold']:
        monitor_Bold = lab.monitors.Bold(
            variables_of_interest=np.array(param_tvb['parameter_Bold']['variables_of_interest']),
            period=param_tvb['parameter_Bold']['period'])
        monitors.append(monitor_Bold)

    #save the parameters in on file
    if not os.path.exists(param_tvb['path_result']):
        os.mkdir(param_tvb['path_result'])
    f = open(param_tvb['path_result']+'/parameter.py',"w")
    for name,dic in [('param_tvb',param_tvb),
                     ('param_zerlaut',param_zerlaut),
                     ('param_nest',param_nest),
                     ('param_topology',param_topology),
                     ('param_connection',param_connection),
                     ('param_background',param_background)
                     ]:
        f.write(name+' = ')
        json.dump(dic, f)
        f.write("\n")
    f.close()
    subprocess.call([os.path.dirname(os.path.abspath(__file__))+'/correct_parameter.sh',param_tvb['path_result']+'/parameter.py']) ##Warning can be don't find the script

    #initialize the simulator:
    simulator = lab.simulator.Simulator(model = model, connectivity = connection,
                                            coupling = coupling, integrator = integrator, monitors = monitors
                                        )
    simulator.configure()
    # save the initial condition
    np.save(param_tvb['path_result']+'/step_init.npy',simulator.history.buffer)
    # end edit
    return simulator

def run_simulation(simulator, time, parameter_tvb):
    '''
    run a simulation
    :param simulator: the simulator already initialize
    :param time: the time of simulation
    :param parameter_tvb: the parameter for the simulator
    '''
    # check how many monitor it's used
    nb_monitor = parameter_tvb['Raw'] + parameter_tvb['TemporalAverage'] + parameter_tvb['Bold']
    # initialise the variable for the saving the result
    save_result =[]
    for i in range(nb_monitor):
        save_result.append([])
    # run the simulation
    count = 0
    for result in simulator(simulation_length=time):
        for i in range(nb_monitor):
            if result[i] is not None:
                save_result[i].append(result[i])
        #save the result in file
        if result[0][0] >= parameter_tvb['save_time']*(count+1): #check if the time for saving at some time step
            print('simulation time :'+str(result[0][0])+'\r')
            np.save(parameter_tvb['path_result']+'/step_'+str(count)+'.npy',save_result)
            save_result =[]
            for i in range(nb_monitor):
                save_result.append([])
            count +=1
    # save the last part
    np.save(parameter_tvb['path_result']+'/step_'+str(count)+'.npy',save_result)

def simulate_tvb(results_path,begin,end,param_tvb,param_zerlaut,
              param_nest,param_topology,param_connection,param_background):
    '''
    simulate TVB with zerlaut simulation
    :param results_path: the folder to save the result
    :param begin: the starting point of record  WARNING : not used
    :param end: the ending point of record
    :param param_tvb: the parameter of tvb
    :param param_zerlaut: parameter for the model
    :param param_nest: parameter for nest
    :param param_topology: parameter for the region
    :param param_connection: parameter for the connections between neurons and regions
    :param param_background: parameters for the noise
    :return: simulation
    '''
    #TODO add the option for the co-simulation (add raw_monitor and manage proxy node) or create another functions
    param_tvb['path_result']=results_path+'/tvb/'
    simulator = init(param_tvb,param_zerlaut,
              param_nest,param_topology,param_connection,param_background)
    run_simulation(simulator,end,param_tvb)


def get_result(path,time_begin,time_end):
    '''
    return the result of the simulation between the wanted time
    :param path: the folder of the simulation
    :param time_begin: the start time for the result
    :param time_end:  the ending time for the result
    :return: result of all monitor
    '''
    sys.path.append(path)
    from parameter import param_tvb
    sys.path.remove(path)
    count_begin = int(time_begin/param_tvb['save_time'])
    count_end = int(time_end/param_tvb['save_time'])+1
    nb_monitor = param_tvb['Raw'] + param_tvb['TemporalAverage'] + param_tvb['Bold']
    output =[]

    for count in range(count_begin,count_end):
        result = np.load(path+'/step_'+str(count)+'.npy',allow_pickle=True)
        for i in range(result.shape[0]):
            tmp = np.array(result[i])
            if len(tmp) != 0:
                tmp = tmp[np.where((time_begin <= tmp[:,0]) &  (tmp[:,0]<= time_end)),:]
                tmp_time = tmp[0][:,0]
                if tmp_time.shape[0] != 0:
                    one = tmp[0][:,1][0]
                    tmp_value = np.concatenate(tmp[0][:,1]).reshape(tmp_time.shape[0],one.shape[0],one.shape[1])
                    if len(output) == nb_monitor:
                        output[i]=[np.concatenate([output[i][0],tmp_time]),np.concatenate([output[i][1],tmp_value])]
                    else:
                        output.append([tmp_time,tmp_value])
    return output
