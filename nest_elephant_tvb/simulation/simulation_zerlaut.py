import nest_elephant_tvb.simulation.file_tvb.Zerlaut as Zerlaut
from nest_elephant_tvb.simulation.file_tvb.Interface_co_simulation_parallel import Interface_co_simulation
import tvb.simulator.lab as lab
import numpy.random as rgn
import numpy as np
import nest_elephant_tvb.simulation.file_tvb.noise as my_noise
from mpi4py import MPI

def init(param_tvb,param_zerlaut,param_nest,param_topology,param_connection,param_background,mpi=None):
    '''
    Initialise the simulator with parameter
    :param param_tvb : parameter for the simulator tvb
    :param param_zerlaut : parameter for the model
    :param param_nest : parameter for the simulator of tvb from nest parameter
    :param param_connection : parameter for the connection between neurons and regions
    :param param_topology : parameter for the neurons and the population
    :param param_background : parameter for the noise
    :param mpi : if use or not mpi
    :return: the simulator initialize
    '''
    ## initialise the random generator
    rgn.seed(param_nest['master_seed']-1)

    ## Model
    if param_zerlaut['order'] == 1:
        model = Zerlaut.ZerlautAdaptationFirstOrder(variables_of_interest='E I W_e W_i'.split())
    elif param_zerlaut['order'] == 2:
        model = Zerlaut.ZerlautAdaptationSecondOrder(variables_of_interest='E I C_ee C_ei C_ii W_e W_i'.split())
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
    # test of noiose should be remove and use paramerters
    noise = my_noise.Ornstein_Ulhenbeck_process(
        tau_OU=20.0,
        # mu=np.array([300.0,0.0,0.,0.0,0.0,0.0,0.0]).reshape((7,1,1)),
        # nsig=np.array([10.0,0.,0.,0.,0.,0.,0.]),
        # weights=np.array([1/400,0.,0.,0.,0.,0.,0.]).reshape((7,1,1))
        mu=np.array([700e-3,0.0,0.,0.0,0.0,0.0,0.0]).reshape((7,1,1)),
        nsig=np.array([50e-3,0.,0.,0.,0.,0.,0.]),
        weights=np.array([1.e-2,0.,0.,0.,0.,0.,0.]).reshape((7,1,1))
    )
    # noise = my_noise.Poisson_noise(nsig=np.array([30.0,0.0,0.,0.,0.,0.0,0.]),
    #                                weights=np.array([3.5e-4,0.,0.,0.,0.,0.,0.]).reshape((7,1,1))) #TODO to remove number
                                    # weights = np.array([5/400*0.1, 0., 1e-6, 0., 0., 0., 0.]).reshape((7, 1, 1)))  # TODO to remove number
    # noise = my_noise.Poisson_noise(nsig=np.array([300.0,300.0,300.,0.,300.,0.,0.]),
    #                                weights=np.array([1./8000.,1./2000.,1./8000./8000.,0.,1./2000./2000.,0.,0.]).reshape((7,1,1))) #TODO to remove number
    # noise = my_noise.Poisson_noise(nsig=np.array([1.0,param_background['rate_in']-200.0*1e-3,0.,0.,0.,0.,0.]),
    #                                nb_neurons=1)
    # noise = lab.noise.Additive(nsig=np.array([3.16*5/400.0*1e-9,0.,0.,0.,0.,0.,0.]))
    # noise = lab.noise.Additive(nsig=np.array([0.0,0.,0.,0.,0.,0.,0.]))
    noise.random_stream.seed(param_nest['master_seed']-1)
    integrator = lab.integrators.HeunStochastic(noise=noise,dt=param_nest['sim_resolution'])
    # integrator = lab.integrators.HeunDeterministic()

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
    if mpi is not None:
        # special monitor for MPI
        monitor_IO = Interface_co_simulation(
           id_proxy=mpi['id_proxy'],
           time_synchronize=mpi['time_synchronize']
            )
        monitors.append(monitor_IO)


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

def rum_mpi(path):
    '''
    return the result of the simulation between the wanted time
    :param path: the folder of the simulation
    '''
    # take the parameters of the simulation frfom the saving file
    sys.path.append(path)
    from parameter import param_co_simulation,param_tvb,param_zerlaut,param_nest,param_topology,param_connection,param_background,result_path,begin,end
    sys.path.remove(path)

    #initialise the TVB
    param_tvb['path_result']=result_path+'/tvb/'
    id_proxy = param_co_simulation['id_region_nest']
    time_synch = param_co_simulation['synchronization']
    simulator = init(param_tvb,param_zerlaut,
              param_nest,param_topology,param_connection,param_background,{'id_proxy':np.array(id_proxy),
                                                                          'time_synchronize':time_synch,
                                                                           })
    # configure for saving result of TVB
    # check how many monitor it's used
    nb_monitor = param_tvb['Raw'] + param_tvb['TemporalAverage'] + param_tvb['Bold']
    # initialise the variable for the saving the result
    save_result =[]
    for i in range(nb_monitor):
        save_result.append([])
    count = 0

    #init MPI :
    data = None #data for the proxy node (no initialisation in the parameter)
    comm_receive=[]
    for i in id_proxy:
        comm_receive.append(init_mpi(result_path+"/send_to_tvb/"+str(i)+".txt"))
    comm_send=[]
    for i in id_proxy :
        comm_send.append(init_mpi(result_path+"/receive_from_tvb/"+str(i)+".txt"))

    # the loop of the simulation
    count = 0
    while count*time_synch < end:
        print("####### TVB start simulation"); sys.stdout.flush()
        nest_data=[]
        for result in simulator(simulation_length=time_synch,proxy_data=data):
            for i in range(nb_monitor):
                if result[i] is not None:
                    save_result[i].append(result[i])
            nest_data.append([result[-1][0][1],result[-1][1][1]])

            #save the result in file
            if result[-1][0][0] >= param_tvb['save_time']*(count+1): #check if the time for saving at some time step
                np.save(param_tvb['path_result']+'/step_'+str(count)+'.npy',save_result)
                save_result =[]
                for i in range(nb_monitor):
                    save_result.append([])
                count +=1
        print("####### TVB end simulation"); sys.stdout.flush()

        # prepare to send data with MPI
        nest_data = np.array(nest_data)
        time = [nest_data[0,0]+time_synch,nest_data[-1,0]+time_synch]
        rate = np.concatenate(nest_data[:,1])
        for index,comm in enumerate(comm_send):
            send_mpi(comm,time,rate[index]*1e3)

        print("####### TVB receive data"); sys.stdout.flush()
        #receive MPI data
        data_value = []
        for comm in comm_receive:
            receive = receive_mpi(comm)
            time_data = receive[0]
            data_value.append(receive[1])
        data=np.empty((2,),dtype=object)
        nb_step = (time_data[0]-time_data[1])/param_nest['sim_resolution']
        time_data = np.arange(0,nb_step,1)*param_nest['sim_resolution']
        data_value = np.swapaxes(np.array(data_value),0,1)[:,:,np.newaxis,np.newaxis]
        if data_value.shape[0] != time_data.shape[0]:
            raise(Exception('Bad shape of data'))
        data[:]=[time_data,data_value]
        #increment of the loop
        count+=1
    # save the last part
    np.save(param_tvb['path_result']+'/step_'+str(count)+'.npy',save_result)
    for index,comm in  enumerate(comm_send):
        end_mpi(comm,result_path+"/send_to_tvb/"+str(id_proxy[index])+".txt")
    for index,comm in  enumerate(comm_receive):
        end_mpi(comm,result_path+"/send_to_tvb/"+str(id_proxy[index])+".txt")

## MPI function for receive and send data

def init_mpi(path):
    """
    initilise MPI connection
    :param path:
    :return:
    """
    fport = open(path, "r")
    port=fport.readline()
    fport.close()
    print("wait connection "+port);sys.stdout.flush()
    comm = MPI.COMM_WORLD.Connect(port)
    print('connect to '+port);sys.stdout.flush()
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
    times = np.array(times,dtype='d') # time of stating and ending step
    comm.Send([times,MPI.DOUBLE],dest=source,tag=0)
    comm.Send([shape,MPI.INT],dest=source,tag=0)
    comm.Send([data, MPI.DOUBLE], dest=source, tag=0)


def receive_mpi(comm):
    """
        receive proxu values the
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

def end_mpi(comm,path):
    """
    ending the communication
    :param comm: MPI communicator
    :param path: for the close the port
    :return: nothing
    """
    # closing the connection at this end
    comm.Disconnect()
    fport = open(path, "r")
    port=fport.readline()
    fport.close()
    print("close connection "+port);sys.stdout.flush()
    MPI.Close_port(port)
    print('exit')
    MPI.Finalize()

if __name__ == "__main__":
    import sys
    if len(sys.argv)==2:
        rum_mpi(sys.argv[1])