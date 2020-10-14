import numpy as np
import sys
import os
import copy

def get_data(path,nb_mpi,labels=['senders','times']):
    '''
    getting data from the result of the tests
    :param path : path of the data
    :param nb_mpi : number of MPI for Nest
    :param labels : labels of the recording device
    '''
    #get data from all the rank
    datas =[]
    for i in range(nb_mpi):
        datas.append(np.load(path + '_rank_' + str(i) + '.npy',allow_pickle=True))
    unite = {}
    for i in labels:
        unite[i]=np.array([])
    data_concatenate = [copy.deepcopy(unite) for i in range(len(datas[0]))]
    for i in range(len(datas[0])):
        for data in datas:
            for label in labels:
                data_concatenate[i][label] = np.concatenate([data_concatenate[i][label],data[i][label]])
    return data_concatenate


def check_recorder(path,nb_mpi,nb_mpi_recorder,devices,separate,index_device,nb_element):
    """
    test the data generate by the recorders
    :param path:path of the files
    :param nb_mpi:number of mpi process
    :param nb_mpi_recorder:number of mpi recorder
    :param devices:number of devices
    :param separate:if the reference recorder are separate or not
    :param index_device:the index of device ( use for define the type of test)
    :param nb_element: the number of element ( use for define he type of test)
    :return: #TODO return if the test succeed or not  and if it failed which part failed
    """
    data_memory = get_data(path + '/recorders_memory' , nb_mpi)
    for index,index_recorder in enumerate(range(1,nb_mpi_recorder+1)):
        data_mpi = np.concatenate(np.load(path + 'recording_mpi_' + str(index_recorder) + '.npy',allow_pickle=True))
        if len(data_mpi) != len(data_memory[index]['times']): # case where the sie of data are different
            print('test Failed')
        else:
            if len(data_mpi)!=0: # case where there are data
                for index_data,d in enumerate(data_mpi):
                    if d[2] - data_memory[index]['times'][index_data] != 0: # case of the time if different
                        print('test Fail')
                        break
                    if separate and ((index_device != -1 and index % nb_element == index_device)  or index_device == -2): # only for the spike generator will break
                        if d[1]+devices - data_memory[index]['senders'][index_data] != 0: # case if the spike_generator has different id
                            print('test Fail')
                            break
                    else:
                        if d[1] - data_memory[index]['senders'][index_data] != 0: # check if the id of the generator of spike is the same
                            print('test Fail')
                            break
                if index_data == len(data_mpi)-1: # test if all the data are tested
                    print('test Succeed')
            else:
                print('test Succeed')


def check_GS_parrot(path,nb_mpi,parrot,separate):
    """
    test spike generator of spike with node
    :param path: path of the files
    :param nb_mpi: number of mpi for Nest
    :param parrot: number of parrot neurons
    :param separate:if the reference generator are separate or not
    :return: #TODO return if the test succeed or not  and if it failed which part failed
    """
    data_memory = get_data(path+'GS_parrot',nb_mpi)
    if len(data_memory) != 0: # if not data don't test
        index = np.unique(data_memory[0]['senders'])
        if separate:
            data_memory_2 = get_data(path+'GS_parrot_bis',nb_mpi)
        times = np.unique(data_memory[0]['times'])
        count =0
        for t in times:
            if separate: # difference case for the reference
                if len(np.where(data_memory_2[0]['times'] == t)[0]) != parrot:         # test if the result is on number of parrot neurons
                    count += 1                                                         # case when there are two spikes
                    if len(np.where(data_memory_2[0]['times'] == t)[0]) % parrot != 0:
                        print('test Fail')                                             # other case failed
            else: # same as previously
                for i in index:
                    if len(np.where(np.logical_and(data_memory[0]['times']==t,data_memory[0]['senders']==i))[0]) != 2:
                        count +=1
                        if len(np.where(np.logical_and(data_memory[0]['times']==t,data_memory[0]['senders']==i))[0]) % 2 !=0:
                            print('test Fail')
        if count > len(data_memory[0]['times'])/parrot/2/10: # 10% can be repeated spikes
            print('test Fail')
        print('test succeed')
    else:
        print('skip test')


def check_GS_spike_device(path,nb_mpi,spike_generator,separate):
    """
    test spike generator of spike with devices
    :param path: path of the files
    :param nb_mpi: number of mpi for Nest
    :param spike_generator: number of spike_generator
    :param separate: if the reference generator are separate or not
    :return: #TODO return if the test succeed or not  and if it failed which part failed
    """
    data_memory = get_data(path+'GS_spike_device',nb_mpi)
    if len(data_memory) != 0: # if not data don't test
        index = np.unique(data_memory[0]['senders'])
        if separate:
            data_memory_2 = get_data(path+'GS_spike_device_bis',nb_mpi)
        times = np.unique(data_memory[0]['times'])
        count =0
        for t in times:
            if separate: # difference case for the reference
                if len(np.where(data_memory_2[0]['times'] == t)[0]) != 1:       # test if the result is present
                    count += 1
                    if len(np.where(data_memory_2[0]['times'] == t)[0]) != 2:   # case when there are two spikes
                        print('test Fail ')                                     # other case failed
            else: # same as previously
                for i in index:
                    if len(np.where(np.logical_and(data_memory[0]['times']==t,data_memory[0]['senders']==i))[0]) != 1:
                        count +=1
                        if len(np.where(np.logical_and(data_memory[0]['times']==t,data_memory[0]['senders']==i))[0]) != 2:
                            print('test Fail')
        if count > len(data_memory[0]['times'])/spike_generator/2/10: # 10% can be repeated element
            print('test Fail')
        print('test succeed')
    else:
        print('skip test')

def check_GS_spike_neuron(path,nb_mpi,neurons,separate):
    """
    test spike generator of spike with neurons model
    :param path: path of the files
    :param nb_mpi: number of mpi for Nest
    :param neurons: number of neurons
    :param separate: if the reference generator are separate or not
    :return: #TODO return if the test succeed or not  and if it failed which part failed
    """
    data_memory = get_data(path+'GS_spike_neuron',nb_mpi)
    if len(data_memory) != 0: # if not data don't test
        index = np.unique(data_memory[0]['senders'])
        if separate:
            data_memory_2 = get_data(path+'GS_spike_neuron_bis',nb_mpi)
        times = np.unique(data_memory[0]['times'])
        count =0
        for t in times:
            if separate: # difference case for the reference
                if len(np.where(data_memory_2[0]['times'] == t)[0]) != 1: # test if the result is present WARNING : need to add the case of 2 spikes
                    print('test Fail ')
            else: # same as previously
                for i in index:
                    if len(np.where(np.logical_and(data_memory[0]['times']==t,data_memory[0]['senders']==i))[0]) != 1: # test if the result is present
                        count +=1
                        if len(np.where(np.logical_and(data_memory[0]['times']==t,data_memory[0]['senders']==i))[0]) != 2: # case when there are two spikes
                            print('test Fail ')                                                                            # other case failed
        if count > len(data_memory[0]['times'])/2/neurons/10: # 10% can be repeated element
            print('test Fail')
        print('test succeed')
    else:
        print('skip test')

def check_GC_parrot(path,nb_mpi,parrot,separate):
    """
    test current generator of spike with node
    :param path: path of the files
    :param nb_mpi: number of mpi for Nest
    :param parrot: number of parrot neurons
    :param separate:if the reference generator are separate or not
    :return: #TODO return if the test succeed or not  and if it failed which part failed
    """
    data_memory = get_data(path+'GC_parrot',nb_mpi,labels=['V_m','senders','times'])
    if len(data_memory) != 0: # if not data don't test
        if separate:
            data_memory_2 = get_data(path+'GC_parrot_bis',nb_mpi,labels=['V_m','senders','times'])
        times = np.unique(data_memory[0]['times'])
        if separate: # difference case for the reference
            for t in times:
                time_index = np.where(data_memory[0]['times']==t)[0] # check if the time are the same
                if len(time_index) != parrot:
                    print('test Fail')
                init_val = data_memory[0]['V_m'][time_index][0] # check if the value are the same
                for i in data_memory_2[0]['V_m'][time_index]:
                    if i != init_val:
                        print('test Fail')
        else: # same as previously
            for t in times:
                time_index = np.where(data_memory[0]['times']==t)[0]
                if len(time_index) != parrot:
                    print('test Fail')
                init_val = data_memory[0]['V_m'][time_index][0]
                for i in data_memory[0]['V_m'][time_index]:
                    if i != init_val:
                        print('test Fail')
        print('test succeed')
    else:
        print('skip test')

def check_GC_spike_device(path,nb_mpi,spike_generator,separate):
    """
    test current generator of spike with devices
    :param path: path of the files
    :param nb_mpi: number of mpi for Nest
    :param spike_generator: number of spike generator
    :param separate:if the reference generator are separate or not
    :return: #TODO return if the test succeed or not  and if it failed which part failed
    """
    data_memory = get_data(path+'GC_device',nb_mpi,labels=['V_m','senders','times'])
    if len(data_memory) != 0: # if not data don't test
        if separate:
            data_memory_2 = get_data(path+'GC_device_bis',nb_mpi,labels=['V_m','senders','times'])
        times = np.unique(data_memory[0]['times'])
        if separate: # difference case for the reference
            for t in times:
                time_index = np.where(data_memory[0]['times']==t)[0] # check if the time are the same
                if len(time_index) != spike_generator:
                    print('test Fail')
                init_val = data_memory[0]['V_m'][time_index][0] # check if the value are the same
                for i in data_memory_2[0]['V_m'][time_index]:
                    if i != init_val:
                        print('test Fail')
        else: # same as previously
            for t in times:
                time_index = np.where(data_memory[0]['times']==t)[0]
                if len(time_index) != spike_generator:
                    print('test Fail')
                init_val = data_memory[0]['V_m'][time_index][0]
                for i in data_memory[0]['V_m'][time_index]:
                    if i != init_val:
                        print('test Fail')
        print('test succeed')
    else:
        print('skip test')

def check_GC_spike_neuron(path,nb_mpi,neurons,separate):
    """
    test current generator of spike with model of neurons
    :param path: path of the files
    :param nb_mpi: number of mpi for Nest
    :param neurons: number of neurons
    :param separate:if the reference generator are separate or not
    :return: #TODO return if the test succeed or not  and if it failed which part failed
    """
    data_memory = get_data(path+'GC_neuron',nb_mpi,labels=['V_m','senders','times'])
    if len(data_memory) != 0: # if not data don't test
        if separate:
            data_memory_2 = get_data(path+'GC_neuron_bis',nb_mpi,labels=['V_m','senders','times'])
        times = np.unique(data_memory[0]['times'])
        if separate: # difference case for the reference
            for t in times:
                time_index = np.where(data_memory[0]['times']==t)[0] # check if the time are the same
                if len(time_index) != neurons:
                    print('test Fail')
                init_val = data_memory[0]['V_m'][time_index][0] # check if the value are the same
                for i in data_memory_2[0]['V_m'][time_index]:
                    if i != init_val:
                        print('test Fail')
        else: # same as previously
            for t in times:
                time_index = np.where(data_memory[0]['times']==t)[0]
                if len(time_index) != neurons:
                    print('test Fail')
                init_val = data_memory[0]['V_m'][time_index][0]
                for i in data_memory[0]['V_m'][time_index]:
                    if i != init_val:
                        print('test Fail')
        print('test succeed')
    else:
        print('skip test')

def check(nb_VP,nb_mpi,nb_run, time_sim,
                   spike_generator=0,parrot=0,iaf=0,
                  separate=False, nb_mpi_recorder=0,
                   nb_mpi_generator_spike=0,nb_mpi_generator_current=0,shared_mpi_input=False,
                   mix_mpi=0,
                   ):
    """
    return all the test for one simulation case
    :param nb_VP: number of virtual process
    :param nb_mpi: number of mpi rank
    :param nb_run: number of run
    :param time_sim: time of 1 run
    :param spike_generator: number of device
    :param parrot: number of parrot neurons
    :param iaf: number of neurons
    :param separate: separation or not of the reference case
    :param nb_mpi_recorder: number of mpi recorder
    :param nb_mpi_generator_spike: number of spike_generator
    :param nb_mpi_generator_current: number of current generator
    :param shared_mpi_input: if the node share input or not
    :param mix_mpi: different case #TODO not yet implemented
    :return:
    """
    print(nb_VP,nb_mpi,nb_run, time_sim,
                   spike_generator,parrot,iaf,
                   nb_mpi_recorder,separate,
                   nb_mpi_generator_spike,nb_mpi_generator_current,shared_mpi_input,
                   mix_mpi); sys.stdout.flush()
    # name of the file
    name = "nb_VP_"+str(nb_VP)+"nb_mpi"+str(nb_mpi)\
           +'_D_'+str(int(spike_generator))+'_P_'+str(int(parrot))+'_N_'+str(int(iaf))\
           +'_R_'+str(nb_mpi_recorder)+'_Separate_'+str(int(separate))\
           +'_GS_'+str(nb_mpi_generator_spike) +'_GC_'+str(nb_mpi_generator_current)\
           +'_SH_'+str(int(shared_mpi_input))+'_SM_'+str(mix_mpi)+'/'
    path =  os.path.dirname(os.path.realpath(__file__))+"/files/"+name

    # compute index and nb element for distinguish the different tests
    nb_element = int(parrot>0) + int(spike_generator>0) + int(iaf>0)
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

    # run all the tests
    check_recorder(path,nb_mpi,nb_mpi_recorder,spike_generator,separate,index_device,nb_element)
    check_GS_parrot(path,nb_mpi,parrot,separate)
    check_GS_spike_device(path,nb_mpi,spike_generator,separate)
    check_GS_spike_neuron(path,nb_mpi,iaf,separate)
    check_GC_parrot(path,nb_mpi,parrot,separate)
    check_GC_spike_device(path,nb_mpi,spike_generator,separate)
    check_GC_spike_neuron(path,nb_mpi,iaf,separate)

if __name__ == "__main__":
    # print('test 1')
    # check(1 ,1 ,3,200.0,2,2,2,True ,2,2,2,False,0)
    # print('test 1')
    # check(16,1 ,3,200.0,2,2,2,False,2,2,2,False,0)
    # print('test 1')
    # check(16,1 ,3,200.0,2,2,2,True ,2,2,2,False,0)
    # print('test 1')
    # check(16,2 ,3,200.0,2,2,2,False,2,2,2,False,0)
    # print('test 1')
    # check(16,2 ,3,200.0,2,2,2,True ,2,2,2,False,0)
    # print('test 1')
    # check(16,4 ,3,200.0,2,2,2,False,2,2,2,False,0)
    # print('test 1')
    # check(16,4 ,3,200.0,2,2,2,True ,2,2,2,False,0)
    # print('test 1')
    # check(16,8 ,3,200.0,2,2,2,False,2,2,2,False,0)
    # print('test 1')
    # check(16,16,3,200.0,2,2,2,True ,2,2,2,False,0)
    # print('test 1')
    # check(16,16,3,200.0,2,2,2,False,2,2,2,False,0)
    # print('test 1')
    # check(16,8 ,3,200.0,2,2,2,True ,2,2,2,False,0)
    # print('test 1')
    # check(1 ,1 ,3,200.0,2,2,2,True ,6,6,6,False,0)
    # print('test 1')
    # check(16,1 ,3,200.0,2,2,2,False,6,6,6,False,0)
    # print('test 1')
    # check(16,1 ,3,200.0,2,2,2,True ,6,6,6,False,0)
    # print('test 1')
    # check(16,2 ,3,200.0,2,2,2,False,6,6,6,False,0)
    # print('test 1')
    # check(16,2 ,3,200.0,2,2,2,True ,6,6,6,False,0)
    # print('test 1')
    # check(16,4 ,3,200.0,2,2,2,False,6,6,6,False,0)
    # print('test 1')
    # check(16,4 ,3,200.0,2,2,2,True ,6,6,6,False,0)
    # print('test 1')
    # check(16,8 ,3,200.0,2,2,2,False,6,6,6,False,0)
    # print('test 1')
    # check(16,16,3,200.0,2,2,2,True ,6,6,6,False,0)
    # print('test 1')
    # check(16,16,3,200.0,2,2,2,False,6,6,6,False,0)
    # print('test 1')
    # check(16,8 ,3,200.0,2,2,2,True ,6,6,6,False,0)
    if len(sys.argv) == 3:
        check(int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),float(sys.argv[4]),
               int(sys.argv[5]),int(sys.argv[6]),int(sys.argv[7]),
               bool(int(sys.argv[8])),int(sys.argv[9]),
               int(sys.argv[10]),int(sys.argv[11]),bool(int(sys.argv[12])),
               int(sys.argv[13])
               )
    else:
        print('bad number of argument')