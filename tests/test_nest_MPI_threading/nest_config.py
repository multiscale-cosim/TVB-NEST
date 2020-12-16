#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import nest
import numpy as np
from tests.test_nest_MPI_threading.helper import generate_spike, generate_current, create_logger

def create_network(path,nb_VP,nb_mpi,nb_run, time_sim,
                   spike_generator=0,parrot=0,iaf=0,
                   nb_mpi_recorder=0,separate=False,
                   nb_mpi_generator_spike=0,nb_mpi_generator_current=0,shared_mpi_input=False,
                   mix_mpi=0,
                   ):
    """
    configure Nest for the testing part
    :param path: path for saving sim
    :param nb_VP: number of virtual processing
    :param nb_mpi: number of MPI rank
    :param nb_run: number of run
    :param time_sim: time of 1 run
    :param spike_generator: number of devices
    :param parrot: number of parrot neurons
    :param iaf: number of model of neurons
    :param nb_mpi_recorder: number of MPI recording
    :param separate: boolean for the separation of not of the reference
    :param nb_mpi_generator_spike: number of mpi generator spike
    :param nb_mpi_generator_current: number of mpi current
    :param shared_mpi_input: shared of the mpi run ( need to valide the test )
    :param mix_mpi: different case #TODO not yet implemented : creation of network where mpi input and output are connected
    :return:
    """
    print(nb_VP,nb_run, time_sim,
                   spike_generator,parrot,iaf,
                   nb_mpi_recorder,separate,
                   nb_mpi_generator_spike,nb_mpi_generator_current,shared_mpi_input,
                   mix_mpi); sys.stdout.flush()
    # name of the test
    name = "nb_VP_"+str(nb_VP)+"nb_mpi"+str(nb_mpi)\
           +'_D_'+str(int(spike_generator))+'_P_'+str(int(parrot))+'_N_'+str(int(iaf))\
           +'_R_'+str(nb_mpi_recorder)+'_Separate_'+str(int(separate))\
           +'_GS_'+str(nb_mpi_generator_spike) +'_GC_'+str(nb_mpi_generator_current)\
           +'_SH_'+str(int(shared_mpi_input))+'_SM_'+str(mix_mpi)
    logger = create_logger(path+'/log/',name='nest_'+str(nest.Rank())) # TODO need to use it for the degging part


    nest.ResetKernel()
    nest.SetKernelStatus({"overwrite_files": True,
                          "data_path": path,
                          "total_num_virtual_procs":nb_VP,
                          })
    # compute index and nb element for distinguish the different tests
    nb_element = int(parrot>0) + int(spike_generator>0) + int(iaf>0)
    if nb_element == 0:
        raise Exception('Miss the configuration '+str(nb_element))
    if shared_mpi_input:
        if nb_mpi_recorder != 0 and nb_mpi_recorder % nb_element !=0:
             raise Exception('Miss nb recorder')
        if nb_mpi_generator_spike != 0 and nb_mpi_generator_spike % nb_element !=0:
            raise Exception('Miss nb spike generator')
        if nb_mpi_generator_current != 0 and nb_mpi_generator_current % nb_element !=0:
            raise Exception('Miss nb current generator')
        index_parrot =-2
        index_device = -2
        index_aif = -2
    else:
        if parrot > 0 :
            index_parrot = 0
            if spike_generator > 0:
                index_device = 1
                if iaf > 0:
                    index_aif = 2
                else:
                    index_aif = -1
            else:
                index_device = -1
                if iaf > 0:
                    index_aif = 1
                else:
                    index_aif = -1
        else:
            index_parrot = -1
            if spike_generator > 0:
                index_device = 0
                if iaf > 0:
                    index_aif = 1
                else:
                    index_aif = -1
            else:
                index_device = -1
                if iaf > 0:
                    index_aif = 0
                else:
                    index_aif = -1

    #create mpi device
    recorders = []
    generator_spike = []
    generator_current = []
    for i in range(nb_mpi_recorder):
        recorders.append(nest.Create("spike_recorder",params={"record_to": "mpi","label": "file_record"}))
    for i in range(nb_mpi_generator_spike):
        generator_spike.append(nest.Create("spike_generator", params={"spike_times": np.array([]), 'stimulus_source': 'mpi',
                                                                      "label": "file_gen_spike"}))
    for i in range(nb_mpi_generator_current):
        generator_current.append(nest.Create("step_current_generator", params={'amplitude_times':np.array([]),
                                             'amplitude_values':np.array([]),
                                             'stimulus_source': 'mpi', "label": "file_gen_current"}))

   # particular device
    poisson_generator=None
    if parrot > 0 and nb_mpi_recorder > 0:
        poisson_generator = nest.Create("poisson_generator")

    # recorder
    recorders_twins = []
    recorder_parrot = []
    recorder_device = []
    recorder_neuron = []
    for i in range(nb_mpi_recorder):
        recorders_twins.append(nest.Create("spike_recorder",params={"record_to": "memory"}))
        if parrot > 0:
            if (index_parrot != -1 and i % nb_element == index_parrot)  or index_parrot == -2:
                recorder_parrot.append( nest.Create('parrot_neuron',parrot))
                nest.Connect(poisson_generator, recorder_parrot[-1])
                nest.Connect(recorder_parrot[-1], recorders[i])
                nest.Connect(recorder_parrot[-1], recorders_twins[i])
        if spike_generator > 0:
            if (index_device != -1 and i % nb_element == index_device)  or index_device == -2:
                np.random.seed(recorders[i].tolist()[0])
                recorder_device.append(nest.Create("spike_generator",spike_generator))
                for j in range(spike_generator):
                    recorder_device[-1][j].set({"spike_times":np.around(np.sort(np.random.rand(100) * time_sim * nb_run), decimals=1).tolist()})
                nest.Connect(recorder_device[-1], recorders[i])
                if separate:
                    np.random.seed(recorders[i].tolist()[0])
                    new_generator = nest.Create("spike_generator", spike_generator)
                    for j in range(spike_generator):
                        new_generator[j].set({"spike_times": np.around(np.sort(np.random.rand(100) * time_sim * nb_run), decimals=1).tolist()})
                    nest.Connect(new_generator, recorders_twins[i])
                else:
                    nest.Connect(recorder_device[-1], recorders_twins[i])
        if iaf > 0:
            if (index_aif != -1 and i % nb_element == index_aif)  or index_aif == -2:
                recorder_neuron.append(nest.Create('iaf_psc_alpha',iaf))
                nest.Connect(poisson_generator, recorder_neuron[-1])
                nest.Connect(recorder_neuron[-1], recorders[i])
                nest.Connect(recorder_neuron[-1], recorders_twins[i])

    # generator spike
    generator_spike_twin = []
    generator_spike_parrot = []
    generator_spike_parrot_bis=None
    if separate:
        generator_spike_parrot_bis = []
    generator_spike_device = []
    generator_spike_device_bis = None
    if separate:
        generator_spike_device_bis = []
    generator_spike_neuron = []
    generator_spike_neuron_bis = None
    if separate:
        generator_spike_neuron_bis = []
    for i in range(nb_mpi_generator_spike):
        data = generate_spike(generator_spike[i].tolist()[0],nb_run,time_sim)[1]
        data = np.concatenate(data).tolist()
        generator_spike_twin.append(nest.Create("spike_generator", params={"spike_times": data}))
        if parrot > 0:
            if (index_parrot != -1 and i % nb_element == index_parrot) or index_parrot == -2:
                new_parrot = nest.Create('parrot_neuron', parrot)
                generator_spike_parrot.append(nest.Create("spike_recorder",params={"record_to": "memory"}))
                nest.Connect(generator_spike[i],new_parrot)
                nest.Connect(new_parrot,generator_spike_parrot[-1])
                if separate:
                    new_parrot_2 = nest.Create('parrot_neuron',parrot)
                    generator_spike_parrot_bis.append(nest.Create("spike_recorder", params={"record_to": "memory"}))
                    nest.Connect(generator_spike_twin[i],new_parrot_2)
                    nest.Connect(new_parrot_2,generator_spike_parrot_bis[-1])
                else:
                    nest.Connect(generator_spike_twin[i], new_parrot)
        if spike_generator > 0:
            if (index_device != -1 and i % nb_element == index_device)  or index_device == -2:
                np.random.seed(generator_spike[-1].tolist()[0])
                generator_spike_device.append(nest.Create("spike_recorder",spike_generator))
                nest.Connect(generator_spike[i],generator_spike_device[-1])
                if separate:
                    generator_spike_device_bis.append(nest.Create("spike_recorder",spike_generator))
                    nest.Connect(generator_spike_twin[i], generator_spike_device_bis[-1])
                else:
                    nest.Connect(generator_spike_twin[i], generator_spike_device[-1])
        if iaf > 0:
            if (index_aif != -1 and i % nb_element == index_aif)  or index_aif == -2:
                neuron_test = nest.Create('iaf_psc_alpha',iaf)
                generator_spike_neuron.append(nest.Create("spike_recorder",1))
                nest.Connect(generator_spike[i],neuron_test)
                nest.Connect(neuron_test,generator_spike_neuron[-1])
                if separate:
                    generator_spike_neuron_bis.append(nest.Create("spike_recorder",1))
                    nest.Connect(generator_spike_twin[i], generator_spike_neuron_bis[-1])
                else:
                    nest.Connect(generator_spike_twin[i], generator_spike_neuron[-1])


    # generator
    generator_current_twin = []
    generator_current_parrot = []
    generator_current_parrot_bis=None
    if separate:
        generator_current_parrot_bis = []
    generator_current_device = []
    generator_current_device_bis = None
    if separate:
        generator_current_device_bis = []
    generator_current_neuron = []
    generator_current_neuron_bis = None
    if separate:
        generator_current_neuron_bis = []
    for i in range(nb_mpi_generator_current):
        data = np.concatenate(generate_current(generator_current[i].tolist()[0],nb_run,time_sim)[1])
        generator_current_twin.append(nest.Create("step_current_generator", params={'amplitude_times':data[:,0],
                                                                                        'amplitude_values':data[:,1],}))
        if parrot > 0:
            if (index_parrot != -1 and i % nb_element == index_parrot)  or index_parrot == -2:
                new_neuron = nest.Create('iaf_cond_alpha', parrot)
                generator_current_parrot.append(nest.Create("multimeter",params={'record_from': ['V_m'],"record_to": "memory"}))
                nest.Connect(generator_current[i],new_neuron)
                nest.Connect(generator_current_parrot[-1],new_neuron)
                if separate:
                    new_neuron_2 = nest.Create('iaf_cond_alpha',parrot)
                    generator_current_parrot_bis.append(nest.Create("multimeter",params={'record_from': ['V_m'],"record_to": "memory"}))
                    nest.Connect(generator_current_twin[i],new_neuron_2)
                    nest.Connect(generator_current_parrot_bis[-1],new_neuron_2)
                else:
                    nest.Connect(generator_current_twin[i], new_neuron)
        if spike_generator > 0:
            if (index_device != -1 and i % nb_element == index_device)  or index_device == -2:
                neuron_test = nest.Create('iaf_cond_alpha',iaf)
                generator_current_device.append(nest.Create("multimeter",params={'record_from': ['V_m'],"record_to": "memory"}))
                nest.Connect(generator_current[i],neuron_test)
                nest.Connect(generator_current_device[-1],neuron_test)
                if separate:
                    neuron_test_2 = nest.Create('iaf_cond_alpha', iaf)
                    generator_current_device_bis.append(nest.Create("multimeter",params={'record_from': ['V_m'],"record_to": "memory"}))
                    nest.Connect(generator_current_device_bis[-1],neuron_test)
                    nest.Connect(generator_current_twin[i],neuron_test_2)
                else:
                    nest.Connect(generator_current_twin[i],neuron_test)
        if iaf > 0:
            if (index_aif != -1 and i % nb_element == index_aif)  or index_aif == -2:
                neuron_test = nest.Create('iaf_psc_alpha',iaf)
                generator_current_neuron.append(nest.Create("multimeter",params={'record_from': ['V_m'],"record_to": "memory"}))
                nest.Connect(generator_current[i],neuron_test)
                nest.Connect(generator_current_neuron[-1],neuron_test)
                if separate:
                    neuron_test_2 = nest.Create('iaf_psc_alpha', iaf)
                    generator_current_neuron_bis.append(nest.Create("multimeter",params={'record_from': ['V_m'],"record_to": "memory"}))
                    nest.Connect(generator_current_neuron_bis[-1],neuron_test)
                    nest.Connect(generator_current_twin[i],neuron_test_2)
                else:
                    nest.Connect(generator_current_twin[i],neuron_test)

    # start simulation
    nest.Prepare()
    for i in range(nb_run):
        nest.Run(time_sim)
    nest.Cleanup()

    # write result in file for the validation
    devices_record_memory = [
        ('recorders_memory',recorders_twins),
        ('GS_parrot',generator_spike_parrot),
        ('GS_parrot_bis',generator_spike_parrot_bis),
        ('GS_spike_device',generator_spike_device),
        ('GS_spike_device_bis',generator_spike_device_bis),
        ('GS_spike_neuron',generator_spike_neuron),
        ('GS_spike_neuron_bis',generator_spike_neuron_bis),
        ('GC_parrot',generator_current_parrot),
        ('GC_parrot_bis',generator_current_parrot_bis),
        ('GC_device',generator_current_device),
        ('GC_device_bis',generator_current_device_bis),
        ('GC_neuron',generator_current_neuron),
        ('GC_neuron_bis',generator_current_neuron_bis)
    ]
    for label, devices in devices_record_memory:
        if devices is not None:
            data_collect = []
            for device in devices:
                for data in nest.GetStatus(device):
                    data_collect.append(data['events'])
            name_save = path+'/'+label + '_rank_' + str(nest.Rank()) + '.npy'
            np.save(name_save,data_collect,allow_pickle=True)


if __name__ == "__main__":
    import sys
    if len(sys.argv)== 15 :
        create_network(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),float(sys.argv[5]),
                       int(sys.argv[6]),int(sys.argv[7]),int(sys.argv[8]),
                       int(sys.argv[9]),bool(int(sys.argv[10])),
                       int(sys.argv[11]),int(sys.argv[12]),bool(int(sys.argv[13])),
                       int(sys.argv[14])
                       )
    else:
        print('missing argument')