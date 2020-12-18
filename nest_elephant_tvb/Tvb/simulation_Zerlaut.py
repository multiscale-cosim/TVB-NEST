#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import logging
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('tvb').setLevel(logging.ERROR)

import tvb.simulator.lab as lab
from tvb.datatypes.sensors import SensorsInternal
import numpy.random as rgn
import numpy as np
from mpi4py import MPI
import os
import json
import time
import nest_elephant_tvb.Tvb.modify_tvb.noise as my_noise
import nest_elephant_tvb.Tvb.modify_tvb.Zerlaut as Zerlaut
from nest_elephant_tvb.Tvb.modify_tvb.Interface_co_simulation_parallel import Interface_co_simulation
from nest_elephant_tvb.Tvb.helper_function_zerlaut import findVec

from timer.Timer import Timer
timer_tvb = Timer(7,100000)

def init(param_tvb_connection,param_tvb_coupling,param_tvb_integrator,param_tvb_model,param_tvb_monitor,cosim=None):
    '''
    Initialise the simulator with parameter
    :param param_tvb_connection : parameters for the connection
    :param param_tvb_coupling : parameters for the coupling between nodes
    :param param_tvb_integrator : parameters of the integrator and the noise
    :param param_tvb_model : parameters for the models of TVB
    :param param_tvb_monitor : parameters for TVB monitors
    :param cosim : if use or not mpi
    :return: the simulator initialize
    '''
    timer_tvb.start(1)
    ## initialise the random generator
    rgn.seed(param_tvb_integrator['seed_init']-1)

    ## Model configuration
    if param_tvb_model['order'] == 1:
        model = Zerlaut.ZerlautAdaptationFirstOrder(variables_of_interest='E I W_e W_i'.split())
    elif param_tvb_model['order'] == 2:
        model = Zerlaut.ZerlautAdaptationSecondOrder(variables_of_interest='E I C_ee C_ei C_ii W_e W_i'.split())
    else:
        raise Exception('Bad order for the model')
    model.g_L=np.array(param_tvb_model['g_L'])
    model.E_L_e=np.array(param_tvb_model['E_L_e'])
    model.E_L_i=np.array(param_tvb_model['E_L_i'])
    model.C_m=np.array(param_tvb_model['C_m'])
    model.b_e=np.array(param_tvb_model['b_e'])
    model.a_e=np.array(param_tvb_model['a_e'])
    model.b_i=np.array(param_tvb_model['b_i'])
    model.a_i=np.array(param_tvb_model['a_i'])
    model.tau_w_e=np.array(param_tvb_model['tau_w_e'])
    model.tau_w_i=np.array(param_tvb_model['tau_w_i'])
    model.E_e=np.array(param_tvb_model['E_e'])
    model.E_i=np.array(param_tvb_model['E_i'])
    model.Q_e=np.array(param_tvb_model['Q_e'])
    model.Q_i=np.array(param_tvb_model['Q_i'])
    model.tau_e=np.array(param_tvb_model['tau_e'])
    model.tau_i=np.array(param_tvb_model['tau_i'])
    model.N_tot=np.array(param_tvb_model['N_tot'])
    model.p_connect=np.array(param_tvb_model['p_connect'])
    model.g=np.array(param_tvb_model['g'])
    model.T=np.array(param_tvb_model['T'])
    model.P_e=np.array(param_tvb_model['P_e'])
    model.P_i=np.array(param_tvb_model['P_i'])
    model.K_ext_e=np.array(param_tvb_model['K_ext_e'])
    model.K_ext_i=np.array(0)
    model.external_input_ex_ex=np.array(0.)
    model.external_input_ex_in=np.array(0.)
    model.external_input_in_ex=np.array(0.0)
    model.external_input_in_in=np.array(0.0)
    model.state_variable_range['E'] =np.array( param_tvb_model['initial_condition']['E'])
    model.state_variable_range['I'] =np.array( param_tvb_model['initial_condition']['I'])
    if param_tvb_model['order'] == 2:
        model.state_variable_range['C_ee'] = np.array(param_tvb_model['initial_condition']['C_ee'])
        model.state_variable_range['C_ei'] = np.array(param_tvb_model['initial_condition']['C_ei'])
        model.state_variable_range['C_ii'] = np.array(param_tvb_model['initial_condition']['C_ii'])
    model.state_variable_range['W_e'] = np.array(param_tvb_model['initial_condition']['W_e'])
    model.state_variable_range['W_i'] = np.array(param_tvb_model['initial_condition']['W_i'])

    ## Connection
    nb_region = int(param_tvb_connection['nb_region'])
    tract_lengths = np.load(param_tvb_connection['path_distance'])
    weights = np.load(param_tvb_connection['path_weight'])
    if 'path_region_labels' in param_tvb_connection.keys():
        region_labels = np.loadtxt(param_tvb_connection['path_region_labels'], dtype=str)
    else:
        region_labels = np.array([], dtype=np.dtype('<U128'))
    if 'path_centers' in param_tvb_connection.keys():
        centers = np.loadtxt(param_tvb_connection['path_centers'])
    else:
        centers = np.array([])
    if 'orientation' in param_tvb_connection.keys() and param_tvb_connection['orientation']:
        orientation = []
        for i in np.transpose(centers):
             orientation.append(findVec(i,np.mean(centers,axis=1)))
        orientation = np.array(orientation)
    else:
       orientation = None
    if 'path_cortical' in param_tvb_connection.keys():
        cortical = np.load(param_tvb_connection['path_cortical'])
    else:
        cortical=None
    connection = lab.connectivity.Connectivity(number_of_regions=nb_region,
                                               tract_lengths=tract_lengths[:nb_region,:nb_region],
                                               weights=weights[:nb_region,:nb_region],
                                               region_labels=region_labels,
                                               centres=centers.T,
                                               cortical=cortical,
                                               orientations=orientation)
    # if 'normalised' in param_tvb_connection.keys() or param_tvb_connection['normalised']:
    #     connection.weights = connection.weights / np.sum(connection.weights, axis=0)
    connection.speed = np.array(param_tvb_connection['velocity'])

    ## Coupling
    coupling = lab.coupling.Linear(a=np.array(param_tvb_coupling['a']),
                                       b=np.array(0.0))

    ## Integrator
    noise = my_noise.Ornstein_Ulhenbeck_process(
        tau_OU=param_tvb_integrator['tau_OU'],
        mu=np.array(param_tvb_integrator['mu']).reshape((7,1,1)),
        nsig=np.array(param_tvb_integrator['nsig']),
        weights=np.array(param_tvb_integrator['weights']).reshape((7,1,1))
    )
    noise.random_stream.seed(param_tvb_integrator['seed'])
    integrator = lab.integrators.HeunStochastic(noise=noise,dt=param_tvb_integrator['sim_resolution'])
    # integrator = lab.integrators.HeunDeterministic()

    ## Monitors
    monitors =[]
    if param_tvb_monitor['Raw']:
        monitors.append(lab.monitors.Raw())
    if param_tvb_monitor['TemporalAverage']:
        monitor_TAVG = lab.monitors.TemporalAverage(
            variables_of_interest=param_tvb_monitor['parameter_TemporalAverage']['variables_of_interest'],
            period=param_tvb_monitor['parameter_TemporalAverage']['period'])
        monitors.append(monitor_TAVG)
    if param_tvb_monitor['Bold']:
        monitor_Bold = lab.monitors.Bold(
            variables_of_interest=np.array(param_tvb_monitor['parameter_Bold']['variables_of_interest']),
            period=param_tvb_monitor['parameter_Bold']['period'])
        monitors.append(monitor_Bold)
    if param_tvb_monitor['SEEG']:
        sensor = SensorsInternal().from_file(param_tvb_monitor['parameter_SEEG']['path'])
        projection_matrix = param_tvb_monitor['parameter_SEEG']['scaling_projection']/np.array(
            [np.linalg.norm(np.expand_dims(i, 1) - centers[:, cortical], axis=0) for i in sensor.locations])
        np.save(param_tvb_monitor['path_result']+'/projection.npy',projection_matrix)
        monitors.append(lab.monitors.iEEG.from_file(
            param_tvb_monitor['parameter_SEEG']['path'],
            param_tvb_monitor['path_result']+'/projection.npy'))
    if cosim is not None:
        # special monitor for MPI
        monitor_IO = Interface_co_simulation(
           id_proxy=cosim['id_proxy'],
           time_synchronize=cosim['time_synchronize']
            )
        monitors.append(monitor_IO)


    #initialize the simulator:
    simulator = lab.simulator.Simulator(model = model, connectivity = connection,
                                            coupling = coupling, integrator = integrator, monitors = monitors
                                        )
    simulator.configure()
    # save the initial condition
    np.save(param_tvb_monitor['path_result']+'/step_init.npy',simulator.history.buffer)
    # end edit
    timer_tvb.stop(1)
    return simulator

def run_simulation(simulator, time, parameter_tvb):
    '''
    run a simulation
    :param simulator: the simulator already initialize
    :param time: the time of simulation
    :param parameter_tvb: the parameter for the simulator
    '''
    # check how many monitor it's used
    nb_monitor = parameter_tvb['Raw'] + parameter_tvb['TemporalAverage'] + parameter_tvb['Bold'] + parameter_tvb['SEEG']
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

def simulate_tvb(results_path,begin,end,param_tvb_connection,param_tvb_coupling,
                 param_tvb_integrator,param_tvb_model,param_tvb_monitor):
    '''
    simulate TVB with zerlaut simulation
    :param results_path: the folder to save the result
    :param begin: the starting point of record  WARNING : not used
    :param end: the ending point of record
    :param param_tvb_connection : parameters for the connection
    :param param_tvb_coupling : parameters for the coupling between nodes
    :param param_tvb_integrator : parameters of the integrator and the noise
    :param param_tvb_model : parameters for the models of TVB
    :param param_tvb_monitor : parameters for TVB monitors
    :return: simulation
    '''
    param_tvb_monitor['path_result']=results_path+'/tvb/'
    simulator = init(param_tvb_connection,param_tvb_coupling,param_tvb_integrator,param_tvb_model,param_tvb_monitor)
    run_simulation(simulator,end,param_tvb_monitor)

def run_mpi(path):
    '''
    return the result of the simulation between the wanted time
    :param path: the folder of the simulation
    '''
    timer_tvb.start(0)
    # take the parameters of the simulation from the saving file
    with open(path+'/parameter.json') as f:
        parameters = json.load(f)
    param_co_simulation = parameters['param_co_simulation']
    param_tvb_connection= parameters['param_tvb_connection']
    param_tvb_coupling= parameters['param_tvb_coupling']
    param_tvb_integrator= parameters['param_tvb_integrator']
    param_tvb_model= parameters['param_tvb_model']
    param_tvb_monitor= parameters['param_tvb_monitor']
    result_path= parameters['result_path']
    end = parameters['end']

    # configuration of the logger
    logger = logging.getLogger('tvb')
    fh = logging.FileHandler(path + '/log/tvb.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    if param_co_simulation['level_log'] == 0:
        fh.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    elif  param_co_simulation['level_log'] == 1:
        fh.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif  param_co_simulation['level_log'] == 2:
        fh.setLevel(logging.WARNING)
        logger.setLevel(logging.WARNING)
    elif  param_co_simulation['level_log'] == 3:
        fh.setLevel(logging.ERROR)
        logger.setLevel(logging.ERROR)
    elif  param_co_simulation['level_log'] == 4:
        fh.setLevel(logging.CRITICAL)
        logger.setLevel(logging.CRITICAL)

    #initialise the TVB
    param_tvb_monitor['path_result']=result_path+'/tvb/'
    id_proxy = param_co_simulation['id_region_nest']
    time_synch = param_co_simulation['synchronization']
    path_send = result_path+"/translation/send_to_tvb/"
    path_receive = result_path+"/translation/receive_from_tvb/"
    simulator = init(param_tvb_connection,param_tvb_coupling,param_tvb_integrator,param_tvb_model,param_tvb_monitor,
                     {'id_proxy':np.array(id_proxy),
                      'time_synchronize':time_synch,
                      'path_send': path_send,
                      'path_receive': path_receive,
                     })
    # configure for saving result of TVB
    # check how many monitor it's used
    nb_monitor = param_tvb_monitor['Raw'] + param_tvb_monitor['TemporalAverage'] + param_tvb_monitor['Bold'] + param_tvb_monitor['SEEG']
    # initialise the variable for the saving the result
    save_result =[]
    for i in range(nb_monitor): # the input output monitor
        save_result.append([])

    #init MPI :
    data = None #data for the proxy node (no initialisation in the parameter)
    comm_receive=[]
    for i in id_proxy:
        comm_receive.append(init_mpi(path_send+str(i)+".txt",logger))
    comm_send=[]
    for i in id_proxy :
        comm_send.append(init_mpi(path_receive+str(i)+".txt",logger))

    # the loop of the simulation
    count = 0
    count_save = 0
    timer_tvb.stop(0)
    while count*time_synch < end: # FAT END POINT
        timer_tvb.start(2)
        logger.info(" TVB receive data")
        #receive MPI data
        data_value = []
        for comm in comm_receive:
            receive = receive_mpi(comm)
            time_data = receive[0]
            data_value.append(receive[1])
        data=np.empty((2,),dtype=object)
        nb_step = np.rint((time_data[1]-time_data[0])/param_tvb_integrator['sim_resolution'])
        nb_step_0 = np.rint(time_data[0]/param_tvb_integrator['sim_resolution']) + 1 # start at the first time step not at 0.0
        time_data = np.arange(nb_step_0,nb_step_0+nb_step,1)*param_tvb_integrator['sim_resolution']
        data_value = np.swapaxes(np.array(data_value),0,1)[:,:]
        if data_value.shape[0] != time_data.shape[0]:
            raise(Exception('Bad shape of data'))
        data[:]=[time_data,data_value]
        timer_tvb.stop(2)

        logger.info(" TVB start simulation "+str(count*time_synch))
        nest_data=[]
        timer_tvb.start(3)
        for result in simulator(simulation_length=time_synch,proxy_data=data):
            for i in range(nb_monitor):
                if result[i] is not None:
                    save_result[i].append(result[i])
            nest_data.append([result[-1][0],result[-1][1]])

            #save the result in file
            if result[-1][0] >= param_tvb_monitor['save_time']*(count_save+1): #check if the time for saving at some time step
                np.save(param_tvb_monitor['path_result']+'/step_'+str(count_save)+'.npy',save_result)
                save_result =[]
                for i in range(nb_monitor):
                    save_result.append([])
                count_save +=1
        timer_tvb.stop(3)
        logger.info(" TVB end simulation")

        # prepare to send data with MPI
        timer_tvb.start(4)
        nest_data = np.array(nest_data)
        time = [nest_data[0,0],nest_data[-1,0]]
        rate = np.concatenate(nest_data[:,1])
        for index,comm in enumerate(comm_send):
            send_mpi(comm,time,rate[:,index]*1e3)
        timer_tvb.stop(4)

        #increment of the loop
        count+=1
    timer_tvb.start(0)
    # save the last part
    logger.info(" TVB finish")
    np.save(param_tvb_monitor['path_result']+'/step_'+str(count_save)+'.npy',save_result)
    for index,comm in  enumerate(comm_send):
        end_mpi(comm,result_path+"/translation/receive_from_tvb/"+str(id_proxy[index])+".txt",True,logger)
    for index,comm in  enumerate(comm_receive):
        end_mpi(comm,result_path+"/translation/send_to_tvb/"+str(id_proxy[index])+".txt",False,logger)
    MPI.Finalize() # ending with MPI
    logger.info(" TVB exit")
    timer_tvb.stop(0)
    timer_tvb.save(path+'/timer_tvb.npy')
    return

## MPI function for receive and send data

def init_mpi(path,logger):
    """
    initialise MPI connection
    :param path:
    :return:
    """
    while not os.path.exists(path+'.unlock'): # FAT END POINT
        logger.info(path+'.unlock')
        logger.info("spike detector ids not found yet, retry in 1 second")
        time.sleep(1)
    os.remove(path+'.unlock')
    fport = open(path, "r")
    port=fport.readline()
    fport.close()
    logger.info("wait connection "+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    logger.info('connect to '+port);sys.stdout.flush()
    return comm

def send_mpi(comm,times,data):
    """
    send mpi data
    :param comm: MPI communicator
    :param times: times of values
    :param data: rates inputs
    :return:nothing
    """
    status_ = MPI.Status()
    # wait until the translator accept the connections
    accept = False
    timer_tvb.start(5)
    while not accept:
        req = comm.irecv(source=0,tag=0)
        accept = req.wait(status_)
    timer_tvb.stop(5)
    source = status_.Get_source() # the id of the excepted source
    data = np.ascontiguousarray(data,dtype='d') # format the rate for sending
    shape = np.array(data.shape[0],dtype='i') # size of data
    times = np.array(times,dtype='d') # time of starting and ending step
    comm.Send([times,MPI.DOUBLE],dest=source,tag=0)
    comm.Send([shape,MPI.INT],dest=source,tag=0)
    comm.Send([data, MPI.DOUBLE], dest=source, tag=0)


def receive_mpi(comm):
    """
        receive proxy values the
    :param comm: MPI communicator
    :return: rate of all proxy
    """
    status_ = MPI.Status()
    # send to the translator : I want the next part
    timer_tvb.start(6)
    req = comm.isend(True, dest=0, tag=0)
    req.wait()
    time_step = np.empty(2, dtype='d')
    comm.Recv([time_step, 2, MPI.DOUBLE], source=0, tag=MPI.ANY_TAG, status=status_)
    timer_tvb.stop(6)
    # get the size of the rate
    size=np.empty(1,dtype='i')
    comm.Recv([size, MPI.INT], source=0, tag=0)
    # get the rate
    rates = np.empty(size, dtype='d')
    comm.Recv([rates,size, MPI.DOUBLE],source=0,tag=MPI.ANY_TAG,status=status_)
    # print the summary of the data
    if status_.Get_tag() == 0:
        return time_step,rates
    else:
        return None # TODO take in count

def end_mpi(comm,path,sending,logger):
    """
    ending the communication
    :param comm: MPI communicator
    :param path: for the close the port
    :param sending: if the translator is for sending or receiving data
    :return: nothing
    """
    # read the port before the deleted file
    fport = open(path, "r")
    port=fport.readline()
    fport.close()
    # different ending of the translator
    if sending :
        logger.info("TVB close connection send " + port)
        sys.stdout.flush()
        status_ = MPI.Status()
        # wait until the translator accept the connections
        logger.info("TVB send check")
        accept = False
        while not accept:
            req = comm.irecv(source=0, tag=0)
            accept = req.wait(status_)
        logger.info("TVB send end simulation")
        source = status_.Get_source()  # the id of the excepted source
        times = np.array([0.,0.],dtype='d') # time of starting and ending step
        comm.Send([times,MPI.DOUBLE],dest=source,tag=1)
    else:
        logger.info("TVB close connection receive " + port)
        # send to the translator : I want the next part
        req = comm.isend(True, dest=0, tag=1)
        req.wait()
    # closing the connection at this end
    logger.info("TVB disconnect communication")
    comm.Disconnect()
    logger.info("TVB close " + port)
    MPI.Close_port(port)
    logger.info("TVB close connection "+port)
    return

def run_normal(path_parameter):
    with open(path_parameter+'/parameter.json') as f:
        parameters = json.load(f)
    begin = parameters['begin']
    end = parameters['end']
    results_path = parameters['result_path']
    simulate_tvb(results_path=results_path, begin=begin, end=end,
                 param_tvb_connection=parameters['param_tvb_connection'],
                 param_tvb_coupling=parameters['param_tvb_coupling'],
                 param_tvb_integrator=parameters['param_tvb_integrator'],
                 param_tvb_model=parameters['param_tvb_model'],
                 param_tvb_monitor=parameters['param_tvb_monitor'])

if __name__ == "__main__":
    import sys
    if len(sys.argv)==3:
        if sys.argv[1] == '0': # run only tvb without mpi
            run_normal(sys.argv[2])
        elif sys.argv[1] == '1': # run tvb in co-simulation configuration
            run_mpi(sys.argv[2])
        else:
            raise Exception('bad option of running')
    else:
        raise Exception('not good number of argument ')
