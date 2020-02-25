from __future__ import print_function
import nest
import numpy as np
import os
import time
import subprocess
import sys

def network_initialisation(results_path,param_nest):
    """
    Initialise the kernel of Nest
    :param results_path: Folder for saving the result of device
    :param param_nest: Dictionary with the parameter for Nest
    :return: Random generator for each thread
    """
    # the seed of the simulation
    master_seed = param_nest['master_seed']
    # the number of processus or thread of the simulation
    total_num_virtual_procs = param_nest['total_num_virtual_procs']
    # Numpy random generator
    np.random.seed(master_seed)
    pyrngs = [np.random.RandomState(s) for s in range(master_seed, master_seed + total_num_virtual_procs)]
    # Nest Kernel
    nest.set_verbosity(param_nest['verbosity'])
    nest.ResetKernel()
    nest.SetKernelStatus({
        # Resolution of the simulation (in ms).
        "resolution": param_nest['sim_resolution'],
        # Print the time progress, this should only be used when the simulation
        # is run on a local machine.
        "print_time": False,
        # If True, data will be overwritten,
        # If False, a NESTError is raised if the files already exist.
        "overwrite_files": True,
        #The number of virtual process for all thread of MPI
        "total_num_virtual_procs": total_num_virtual_procs,
        # "local_num_threads": total_num_virtual_procs,
        # Path to save the output data
        'data_path': results_path,
        # Masterseed for NEST and NumPy
        'grng_seed': master_seed + total_num_virtual_procs,
        # Seeds for the individual processes
        'rng_seeds': range(master_seed + 1 + total_num_virtual_procs, master_seed + 1 + (2 * total_num_virtual_procs)),
    })
    if nest.Rank()==0:
        nest.SetKernelStatus({"print_time": True})
    return pyrngs

def network_initialisation_neurons(results_path,pyrngs,param_topology,return_gids=False,cosimulation=None):
    """
    Create all neuron in each unit in Nest. An unit is composed by two populations (excitatory and inhibitory)
    :param results_path: Folder for saving the result of device
    :param pyrngs: Random generator for each thread
    :param param_topology: Dictionary with the parameter for the topology
    :param return_gids: Boolean to choose to return the ids of population or not
    :param cosimulation : parameters for the  co-simulation
    :return: Dictionary with the id of different layer and the index of the layer out
    """
    # Number of region to simulate
    if cosimulation is not None:
        nb_region =  len(cosimulation['id_region_nest'])
    else:
        nb_region = param_topology['nb_region']

    # Number of neurons by region
    nb_neuron_region = param_topology['nb_neuron_by_region']
    # Percentage of inhibitory neurons
    percentage_inhibitory = param_topology['percentage_inhibitory']
    # Type of neuron
    neuron_type = param_topology['neuron_type']
    # Parameter of excitatory neuron (different to default value)
    params_ex = param_topology['param_neuron_excitatory']
    neuron_type_ex ='excitatory'
    # Parameter of excitatory neuron (different to default value)
    params_in = param_topology['param_neuron_inhibitory']
    neuron_type_in ='inhibitory'
    # Mean of external input
    mean_I_ext = param_topology['mean_I_ext']
    # Sigma of external input
    sigma_I_ext = param_topology['sigma_I_ext']
    # Sigma of initial voltage
    sigma_init_V0 = param_topology['sigma_V_0']
    # mean of initial voltage
    mean_init_w0 = param_topology['mean_w_0']

    # Initialisation of the neuron type
    nest.CopyModel(neuron_type,neuron_type_ex)
    nest.SetDefaults(neuron_type_ex, params_ex)
    nest.CopyModel(neuron_type,neuron_type_in)
    nest.SetDefaults(neuron_type_in, params_in)

    # Create all Units
    nb_ex = int(nb_neuron_region*(1-percentage_inhibitory)) # number of excitatory neurons
    nb_in = int(nb_neuron_region*percentage_inhibitory) # number of inhibitory neurons
    list_region_ex = [] # List of excitatory population
    list_region_in = [] # List of inhibitory population
    gids_ex = [] # save the Id of all excitatory population
    gids_in = [] # save the Id of all inhibitory population
    previous_layer = 0  # Counter for the Id of region

    for j in range(0, nb_region):
        #Excitatory region
        reg_ex = nest.Create(neuron_type_ex, nb_ex)
        list_region_ex.append({'region': reg_ex, 'index':j, 'nb_neurons':nb_ex})
        gids_ex.append([previous_layer, previous_layer + nb_ex])
        previous_layer = previous_layer + nb_ex
        if sigma_I_ext > 0:
            reg_ex.set(I_e=nest.random.normal(mean=mean_I_ext,std=sigma_I_ext))
        else:
            reg_ex.set(I_e=mean_I_ext)
        if sigma_init_V0>0:
            reg_ex.set(V_m=nest.random.normal(mean=nest.GetDefaults(neuron_type_ex)['E_L'],std=sigma_init_V0))
        else:
            reg_ex.set(V_m=nest.GetDefaults(neuron_type_ex)['E_L'] )
        if mean_init_w0 >0:
            reg_ex.set(w=nest.random.normal(mean=mean_init_w0,std=mean_init_w0))
        else:
           reg_ex.set(w=mean_init_w0)

        # Inhibitory region
        reg_in = nest.Create(neuron_type_in, nb_in)
        list_region_in.append({'region': reg_in, 'index':j, 'nb_neurons':nb_in})
        gids_in.append([previous_layer, previous_layer + nb_in])
        previous_layer = previous_layer + nb_in
        if sigma_I_ext > 0:
            reg_in.set(I_e=nest.random.normal(mean=mean_I_ext,std=sigma_I_ext))
        else:
            reg_in.set(I_e=mean_I_ext)
        if sigma_init_V0>0:
            reg_in.set(V_m=nest.random.normal(mean=nest.GetDefaults(neuron_type_in)['E_L'],std=sigma_init_V0))
        else:
            reg_in.set(V_m=nest.GetDefaults(neuron_type_in)['E_L'] )

    dic_layer = {'excitatory': {'list':list_region_ex,'nb':nb_ex}, 'inhibitory': {'list':list_region_in,'nb':nb_in}}

    # save id of each population
    if nest.Rank() == 0:
        pop_file = open(os.path.join(results_path, 'population_GIDs.dat'), 'w+')
        for gid in gids_ex:
            pop_file.write('%d  %d %s\n' % (gid[0], gid[1],'excitatory'))
        for gid in gids_in:
            pop_file.write('%d  %d %s\n' % (gid[0], gid[1],'inhibitory'))
        pop_file.close()

    if return_gids:
        return dic_layer,gids_ex + gids_in
    else:
        return dic_layer

def init_connection(dic_layer,param_topology,param_connection):
    """
    Create the connection between all the neurons
    :param dic_layer: Dictionary with all the layer
    :param param_topology: Parameter for the topology
    :param param_connection: Parameter for the connections
    :return: nothing
    """
    ## Connection inside all region

    #type of synapse
    nest.CopyModel("static_synapse", "excitatory_inside",
                   {"weight":param_connection['weight_local'],
                    "delay":nest.GetKernelStatus("min_delay")})
    nest.CopyModel("static_synapse", "inhibitory_inside",
                   {"weight":- param_connection['g'] * param_connection['weight_local'],
                    "delay":nest.GetKernelStatus("min_delay")})

    #type of connection
    conn_params_ex_inside = {'rule': 'fixed_indegree', 'indegree':int(param_connection['p_connect']* int(param_topology['nb_neuron_by_region']* (1-param_topology['percentage_inhibitory'])))}
    conn_params_in_inside = {'rule': 'fixed_indegree', 'indegree':int(param_connection['p_connect']* int(param_topology['nb_neuron_by_region']* param_topology['percentage_inhibitory']))}

    # connection between each population
    list_layer_ex = dic_layer['excitatory']['list']
    list_layer_in = dic_layer['inhibitory']['list']
    weights = np.load(param_connection['path_weight'])
    delays = np.around(np.load(param_connection['path_distance'])*param_connection['velocity']/nest.GetKernelStatus('resolution'))*nest.GetKernelStatus('resolution')
    delays[np.where(delays<=0.0)]=nest.GetKernelStatus("min_delay")
    return (    conn_params_ex_inside, conn_params_in_inside,
                list_layer_ex,list_layer_in,
                weights,delays)

def create_homogenous_connection(dic_layer,param_connection,save=False,init=None):
    '''
    creation of homogeneous connections or inside population
    :param dic_layer: Dictionary with all the layer
    :param param_connection: Parameter for the connections
    :param save: option for saving or not the connection between neurons
    :param init: option for the initialisation of parameter for the connection
    :return: nothing
    '''
    if init == None:
        (      conn_params_ex_inside, conn_params_in_inside,
               list_layer_ex,list_layer_in,
               weights,delays)= init_connection(dic_layer,param_connection)
    else:
       (       conn_params_ex_inside, conn_params_in_inside,
               list_layer_ex,list_layer_in,
               weights,delays)=init

    #connection inside population of neurons
    for i in range(len(list_layer_ex)):
        if nest.Rank() == 0:
            tic = time.time()
            print('homogenous connection between population not mesh :' + str(i),file=sys.stderr)
        nest.Connect(list_layer_ex[i]['region'], list_layer_ex[i]['region'], conn_spec=conn_params_ex_inside, syn_spec="excitatory_inside")
        nest.Connect(list_layer_ex[i]['region'], list_layer_in[i]['region'], conn_spec=conn_params_ex_inside, syn_spec="excitatory_inside")
        nest.Connect(list_layer_in[i]['region'], list_layer_ex[i]['region'], conn_spec=conn_params_in_inside, syn_spec="inhibitory_inside")
        nest.Connect(list_layer_in[i]['region'], list_layer_in[i]['region'], conn_spec=conn_params_in_inside, syn_spec="inhibitory_inside") #no link between inhibitory neurons
        if nest.Rank() == 0:
            toc = time.time() - tic
            print("Time: %.2f s" % toc, file=sys.stderr)
    if save:
        np.save(param_connection['path_homogeneous']+str(nest.Rank())+'.npy',np.array(nest.GetConnections())[:,:2])

def create_heterogenous_connection(dic_layer,param_topology,param_connection,save=False,init=None, cosimulation=None):
    '''
    creation of heterogenous connections or inside population
    :param dic_layer: Dictionary with all the layer
    :param param_topology: Parameter for the topology
    :param param_connection: Parameter for the connections
    :param save: option for saving or not the connection between neurons
    :param cosimulation : parameters for the  co-simulation
    :return:
    '''
    if init == None:
        (  conn_params_ex_inside, conn_params_in_inside,
           list_layer_ex,list_layer_in,
           weights,delays)= init_connection(dic_layer,param_connection)
    else:
        (conn_params_ex_inside, conn_params_in_inside,
         list_layer_ex,list_layer_in,
         weights,delays)=init
        
    if cosimulation is not None:
        # addapt the weight of the nest node only
        weights=weights[cosimulation['id_region_nest'],:]
        weights=weights[:,cosimulation['id_region_nest']]
        delays=delays[cosimulation['id_region_nest'],:]
        delays=delays[:,cosimulation['id_region_nest']]

    ## connection between region
    for i in range(len(list_layer_ex)):
        if nest.Rank() == 0:
            tic = time.time()
            print('connection between layer :'+str(i),file=sys.stderr)
        # compute the number of synapse receiving by the regions
        nb_synapses = param_topology['nb_neuron_by_region'] * param_connection['nb_external_synapse']
        total_weights =  np.sum(weights[:,i])
        # connect region
        for j in range(len(list_layer_ex)):
            if i != j:
                nb_connection = int( nb_synapses*weights[j,i]/total_weights )
                #rest of the connection and population of neurons
                if nb_connection > 0:
                        # only project excitatory
                        neurons_source = list_layer_ex[j]['region']
                        neurons_target = list_layer_ex[i]['region'] + list_layer_in[i]['region']
                        nest.Connect(neurons_source,neurons_target,
                                     conn_spec={'rule': 'fixed_total_number',
                                                'N': nb_connection},
                                     syn_spec={
                                         #"model": "static_synapse",
                                               "weight":param_connection['weight_global'],
                                               "delay":delays[j,i],
                                               }
                                     )
        if nest.Rank() == 0:
            toc = time.time() - tic
            print("Time: %.2f s" % toc, file=sys.stderr)
    if save:
        np.save(param_connection['path_heterogeneous']+str(nest.Rank())+'.npy',np.array(nest.GetConnections())[:,:2])

def network_connection(dic_layer,param_topology,param_connection, cosimulation=None):
    """
    Create the connection between all the neurons
    :param dic_layer: Dictionary with all the layer
    :param param_topology: Parameter for the topology
    :param param_connection: Parameter for the connections
    :param cosimulation : parameters for the  co-simulation
    :return: nothing
    """
    init= init_connection(dic_layer,param_topology,param_connection)

    create_homogenous_connection(dic_layer,param_connection,save=False,init=init)
    create_heterogenous_connection(dic_layer,param_topology,param_connection,save=False,init=init,cosimulation=cosimulation)


def network_device(dic_layer,min_time,time_simulation,param_background,param_connection,mpi=False,cosimulation=None):
    """
    Create and Connect different record or input device
    :param dic_layer: Dictionary with all the layer
    :param multimeter_record: Boolean for not if we need to record or not the membrane voltmeter
    :param min_time: Beginning time of recording
    :param time_simulation: End of simulation
    :param param_background: parameter for the noise and external input
    :param cosimulation : parameters for the  co-simulation
    :return: the list of multimeter and spike detector
    #TODO : add multimeter and dc_current
    """
    #Spike Detector
    #parameter of spike detector
    if mpi or cosimulation is not None:
       param_spike_dec= {"start": min_time,
                          "stop": time_simulation,
                          "record_to": "mpi",
                          'label': 'spike_detector'
                          }
       nest.CopyModel('spike_detector', 'spike_detector_record_mpi')
       nest.SetDefaults("spike_detector_record_mpi", param_spike_dec)
       spike_detector=[]
    else:
        param_spike_dec= {"start": min_time,
                          "stop": time_simulation,
                          #"withtime": True,
                          #"withgid": True,
                          #'to_file': True,
                          #'to_memory': False,
                          "record_to":"ascii",
                          'label': "spike_detector"
                          }
        nest.CopyModel('spike_detector','spike_detector_record')
        nest.SetDefaults("spike_detector_record",param_spike_dec)
        #list_record
        spike_detector = nest.Create('spike_detector_record')

    # #  Multimeter
    # dict_multimeter = {}
    # # parameter of the multimeter
    # param_mul = {"start": min_time,
    #              "stop": time_simulation,
    #              "interval": 0.1,
    #              "record_from": ["V_m",'w'],
    #              "withtime": True,
    #              'to_accumulator': True,
    #              }

    #Connection to population
    for name_pops,items in dic_layer.items():
        list_pops = items['list']
        for i in range(len(list_pops)):
            # if param_background['multimeter']:
            #     multimeter = nest.Create("multimeter")
            #     param_mul['label'] = name_pops+"_"+str(i)+"/multimeter"
            #     nest.SetStatus(multimeter, param_mul)
            #     nest.Connect(multimeter, list_pops[i]['region'])
            #     dict_multimeter[name_pops].append(
            #         {'detector': multimeter, 'numero': i})
            if mpi:
                spike_detector_mpi = nest.Create('spike_detector_record_mpi')
                spike_detector.append(spike_detector_mpi)
                nest.Connect(list_pops[i]['region'],spike_detector_mpi)
            elif cosimulation is not None:
                if name_pops == 'excitatory':
                    spike_detector_mpi = nest.Create('spike_detector_record_mpi')
                    spike_detector.append(spike_detector_mpi)
                    nest.Connect(list_pops[i]['region'],spike_detector_mpi)
            else:
                nest.Connect(list_pops[i]['region'],spike_detector)

    # create and connect device
    ##External current input
    # external generator
    # if param_background['stimulus']:
    #     param_dc = {"amplitude": param_background['stimulus_amplitude'],
    #                 "start": param_background['stimulus_start'],
    #                 "stop": param_background['stimulus_start']+param_background['stimulus_duration']}
    #     nest.CopyModel("dc_generator",'dc_stim')
    #     nest.SetDefaults("dc_stim",param_dc)
    #     dc_stim = nest.Create('dc_stim',1)
    #     nest.Connect(dc_stim,dic_layer['excitatory']['list'][param_background['stimulus_target']]['region'],{'connection_type': 'divergent'})


    #poisson_generator input
    if param_background['poisson']:
        param_poisson_generator_ex = {
            "rate": param_background['rate_ex'],
            "start": 0.0,
            "stop": time_simulation}
        nest.CopyModel("poisson_generator",'poisson_generator_ex_by_population')
        nest.SetDefaults('poisson_generator_ex_by_population',param_poisson_generator_ex)
        param_poisson_generator_in = {
            "rate": param_background['rate_in'],
            "start": 0.0,
            "stop": time_simulation}
        nest.CopyModel("poisson_generator",'poisson_generator_in_by_population')
        nest.SetDefaults('poisson_generator_in_by_population',param_poisson_generator_in)

        syn_spec_ex_poisson_generator ={
                        'weight' :param_background['weight_poisson'],
                        'delay' : nest.GetKernelStatus("min_delay"), # without delay
                        }
        syn_spec_in_poisson_generator ={
            'weight' :-param_background['weight_poisson']*param_connection['g'],
            'delay' : nest.GetKernelStatus("min_delay"), # without delay
        }
        for name_pops,list_pops in dic_layer.items():
            for index,population in enumerate(list_pops['list']):
                poisson_generator = nest.Create('poisson_generator_ex_by_population')
                nest.Connect(poisson_generator,population['region'],syn_spec=syn_spec_ex_poisson_generator)
                # poisson_generator = nest.Create('poisson_generator_in_by_population')
                # nest.Connect(poisson_generator,population['region'],syn_spec=syn_spec_in_poisson_generator)

    #add noise in current
    if param_background['noise']:
        param_noise_generator = {
            "mean":param_background['mean_noise'],
            "std": param_background['sigma_noise'],
            'dt':nest.GetKernelStatus('resolution'),
            "start": 0.0,
            "stop": time_simulation}
        nest.CopyModel("noise_generator",'noise_generator_global')
        nest.SetDefaults('noise_generator_global',param_noise_generator)
        conndict_noise = {'connection_type': 'divergent',
                       'weights' :param_background['weight_noise'],
                       'delays' : nest.GetKernelStatus("min_delay"), # without delay
                        }
        syn_spec_noise ={
            'weight' :param_background['weight_noise'],
            'delay' : nest.GetKernelStatus("min_delay"), # without delay
        }

        for name_pops,list_pops in dic_layer.items():
            for index,population in enumerate(list_pops['list']):
                noise_generator = nest.Create('noise_generator_global')
                nest.Connect(noise_generator,population['region'],syn_spec=syn_spec_noise)

    #Connection proxy to each neurons
    spike_generator=[]
    if cosimulation is not None:
        param_spike_dec= {"start": 0.0,
                      "stop": time_simulation,
                      "input_from": "mpi",
                      'label': 'spike_generator'
                      }
        nest.CopyModel('spike_generator', 'spike_generator_mpi')
        nest.SetDefaults("spike_generator_mpi", param_spike_dec)
        nb_neurons = []
        name_pops = []
        for name_pop, items in dic_layer.items():
            nb_neurons.append(items['nb'])
            name_pops.append(name_pop)
        for i in range(len(cosimulation['id_region_nest'])):
            spike_generator_mpi = nest.Create('spike_generator_mpi',np.sum(nb_neurons))
            spike_generator.append(spike_generator_mpi)
            nb_device = 0
            for index,name in enumerate(name_pops):
                print([nb_device,nb_device+nb_neurons[index]]);sys.stdout.flush()
                nest.Connect(spike_generator_mpi[nb_device:nb_device+nb_neurons[index]],dic_layer[name]['list'][i]['region'],syn_spec={
                                               "weight":param_connection['weight_global'],
                                               "delay":nest.GetKernelStatus("min_delay"),
                                               },
                            conn_spec={'rule': 'one_to_one'},
                             )
                nb_device+=nb_neurons[index]

    return spike_detector,spike_generator


def simulate (results_path,begin,end,
              param_nest,param_topology,param_connection,param_background):
    """
    Run one simulation of simple network
    :param results_path: the name of file for recording
    :param begin : time of beginning to record
    :param end : time of end simulation
    :param param_nest: Dictionary with the parameter for Nest
    :param param_topology: Parameter for the topology
    :param param_connection: Parameter for the connections
    :param param_background: parameter for the noise and external input
    """
    # Initialisation of the network
    if nest.Rank() == 0:
        tic = time.time()
    pyrngs=network_initialisation(results_path,param_nest)
    dic_layer=network_initialisation_neurons(results_path,pyrngs,param_topology)
    if nest.Rank() == 0:
        toc = time.time() - tic
        print("Time to initialize the network: %.2f s" % toc)

    # Connection and Device
    if nest.Rank() == 0:
        tic = time.time()
    network_connection(dic_layer,param_topology,param_connection)
    spike_detector,spike_generator=network_device(dic_layer,begin,end,param_background,param_connection)
    if nest.Rank() == 0:
        toc = time.time() - tic
        print("Time to create the connections and devices: %.2f s" % toc)

    # Simulation
    if nest.Rank() == 0:
        tic = time.time()
    nest.Simulate(end)
    if nest.Rank() == 0:
        toc=time.time()-tic
        print("Time to simulate: %.2f s" % toc)

def config_mpi_record (results_path,begin,end,
              param_nest,param_topology,param_connection,param_background,
                       cosimulation=None):
    """
    configuration before running
    :param results_path: the name of file for recording
    :param begin : time of beginning to record
    :param end : time of end simulation
    :param param_nest: Dictionary with the parameter for Nest
    :param param_topology: Parameter for the topology
    :param param_connection: Parameter for the connections
    :param param_background: parameter for the noise and external input
    :param cosimulation: parameters for the cosimulation
    """
   # Initialisation of the network
    if nest.Rank() == 0:
        tic = time.time()
    pyrngs=network_initialisation(results_path,param_nest)
    dic_layer=network_initialisation_neurons(results_path,pyrngs,param_topology,cosimulation=cosimulation)
    if nest.Rank() == 0:
        toc = time.time() - tic
        print("Time to initialize the network: %.2f s" % toc)

    # Connection and Device
    if nest.Rank() == 0:
        tic = time.time()
    network_connection(dic_layer,param_topology,param_connection,cosimulation=cosimulation)
    spike_detector,spike_generator=network_device(dic_layer,begin,end,param_background,param_connection,mpi=False,cosimulation=cosimulation)
    if nest.Rank() == 0:
        toc = time.time() - tic
        print("Time to create the connections and devices: %.2f s" % toc)
    return spike_detector,spike_generator

def simulate_mpi_record(end):
    """
     simulation with mpi recording
    :param end : time of end simulation
    """
    # Simulation
    if nest.Rank() == 0:
        tic = time.time()
    nest.Simulate(end)
    if nest.Rank() == 0:
        toc=time.time()-tic
        print("Time to simulate: %.2f s" % toc)

def simulate_mpi_co_simulation(time_synch,end):
    """
    simulation with co-simulation
    :param time_synch: time of synchronization between all the simulator
    :param end : time of end simulation
    """
    # Simulation
    if nest.Rank() == 0:
        tic = time.time()
    count = 0.0
    print("############ Nest Prepare");sys.stdout.flush()
    nest.Prepare()
    while  count*time_synch < end:
        print("############ Nest run "+str(nest.Rank())+" time "+str(nest.GetKernelStatus('time')));sys.stdout.flush()
        nest.Run(time_synch)
        print("############ Nest end");sys.stdout.flush()
        count+=1
    nest.Cleanup()
    if nest.Rank() == 0:
        toc=time.time()-tic
        print("Time to simulate: %.2f s" % toc)