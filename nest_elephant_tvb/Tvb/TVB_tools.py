import logging
logging.getLogger('numba').setLevel(logging.WARNING)
logging.getLogger('tvb').setLevel(logging.ERROR)
from mpi4py import MPI
import os
import json
import time
import numpy as np
import sys

def run_normal(init,path_parameter):
    '''
    return the result of the simulation between the wanted time
    :param init: initialisation function for configure TVB
    :param path_parameter: the folder of the simulation
    '''
    with open(path_parameter+'/parameter.json') as f:
        parameters = json.load(f)
    begin = parameters['begin']
    end = parameters['end']
    results_path = parameters['result_path']
    simulate_tvb(init,results_path=results_path, begin=begin, end=end,
                 param_tvb_connection=parameters['param_tvb_connection'],
                 param_tvb_coupling=parameters['param_tvb_coupling'],
                 param_tvb_integrator=parameters['param_tvb_integrator'],
                 param_tvb_model=parameters['param_tvb_model'],
                 param_tvb_monitor=parameters['param_tvb_monitor'])


def simulate_tvb(init,results_path,begin,end,param_tvb_connection,param_tvb_coupling,
                 param_tvb_integrator,param_tvb_model,param_tvb_monitor):
    '''
    simulate TVB with zerlaut simulation
    :param init: initialisation function for configure TVB
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
    while not accept:
        req = comm.irecv(source=0,tag=0)
        accept = req.wait(status_)
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
    req = comm.isend(True, dest=0, tag=0)
    req.wait()
    time_step = np.empty(2, dtype='d')
    comm.Recv([time_step, 2, MPI.DOUBLE], source=0, tag=MPI.ANY_TAG, status=status_)
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


def run_mpi(init,path):
    '''
    return the result of the simulation between the wanted time
    :param init: initialisation function for configure TVB
    :param path: the folder of the simulation
    '''
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
    time_synch_n = int(np.around(param_co_simulation['synchronization']/param_tvb_integrator['sim_resolution']))
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

    logger.info(" Send initialisation value TVB")
    # prepare to send data with MPI
    nest_data = simulator.output_co_sim_monitor(0, time_synch_n)[0]
    time = [nest_data[0][0], nest_data[0][-1]]
    rate = np.concatenate(nest_data[1][:,0,[id_proxy],0])
    for index, comm in enumerate(comm_send):
        send_mpi(comm, time, rate[:, index] * 1e3)

    # the loop of the simulation
    count = 0
    count_save = 0
    while count*time_synch < end: # FAT END POINT


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

        logger.info(" TVB start simulation "+str(count*time_synch))
        for result in simulator(cosim_updates=data):
            for i in range(nb_monitor):
                if result[i] is not None:
                    save_result[i].append(result[i])

            #save the result in file
            if result[-1][0] >= param_tvb_monitor['save_time']*(count_save+1): #check if the time for saving at some time step
                np.save(param_tvb_monitor['path_result']+'/step_'+str(count_save)+'.npy',save_result)
                save_result =[]
                for i in range(nb_monitor):
                    save_result.append([])
                count_save +=1
        logger.info(" TVB end simulation")

        #increment of the loop
        count+=1

        # prepare to send data with MPI
        nest_data = simulator.output_co_sim_monitor(count*time_synch_n, time_synch_n)[0]
        time = [nest_data[0][0], nest_data[0][-1]]
        rate = np.concatenate(nest_data[1][:, 0, [id_proxy], 0])
        for index, comm in enumerate(comm_send):
            send_mpi(comm, time, rate[:, index] * 1e3)

    # save the last part
    logger.info(" TVB finish")
    np.save(param_tvb_monitor['path_result']+'/step_'+str(count_save)+'.npy',save_result)
    for index,comm in  enumerate(comm_send):
        end_mpi(comm,result_path+"/translation/receive_from_tvb/"+str(id_proxy[index])+".txt",True,logger)
    for index,comm in  enumerate(comm_receive):
        end_mpi(comm,result_path+"/translation/send_to_tvb/"+str(id_proxy[index])+".txt",False,logger)
    MPI.Finalize() # ending with MPI
    logger.info(" TVB exit")
    return
