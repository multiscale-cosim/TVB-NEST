#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
import os
import re

class Node:
    """
    The class for the structure of the tree
    """
    def __init__(self,name,time=0.0,values=None,print_name=None):
        """
        The initialisation of the node
        :param name: the name of the node for getting it
        :param time: the time of the execution of the node
        :param values: the values for each step if it's need it
        :param print_name: the name to print if it's different to the name of the node ( use mainly for long node)
        """
        self.name = name
        if print_name is None:
            self.print_name = self.name
        else:
            self.print_name = print_name
        if values is not None:
            self.values = values
            self.time = np.sum(values)
        else:
            self.time = time
        self.child = []

    def add(self,node):
        """
        add a child to the node
        :param node: the child node
        """
        self.child.append(node)

    def adds(self,*args):
        """
        adds multiple nodes
        :param args: list of node
        """
        for node in args:
            self.child.append(node)

    def addNode(self,*args,**kwargs):
        """
        create a node and add ti the list of child
        :param args: the argument for the node
        :param kwargs: the option for the node
        :return:
        """
        self.child.append(Node(*args,**kwargs))

    def get(self,name):
        """
        get a child by it's name
        :param name: name of the child
        :return:
        """
        for node in self.child:
            if node.name == name:
                return node

    def get_position(self,name):
        """
        get the position of child
        :param name: name of the child
        :return:
        """
        count = 0
        for node in self.child:
            if node.name == name:
                return count
            else:
                count+=1

    def to_array_for_print(self):
        """
        return an array for plotting or print it the tree ( recursive function)
        :return: values ( times of nodes), labels (name of the node), parents ( the parents node)
        """
        values = [self.time]
        labels = [self.print_name]
        parents = ['']
        for child in self.child:
            value_child,labels_child,parents_child = child.to_array_for_print()
            parents_child[0] = self.print_name
            values += value_child
            labels += labels_child
            parents += parents_child
        return values,labels,parents


def get_time(array):
    """
    return the time of the timer
    :param array: array of time start and stop
    :return: the difference between start and stop
    """
    if len(array.shape) == 1:
        return np.diff(array)[np.arange(0,array.shape[-1],2)]
    if len(array.shape) == 2:
        return np.diff(array)[:,np.arange(0,array.shape[-1],2)]


def get_nest_time(array):
    """
    same than previous for nest timer
    :param array: array of time start and stop
    :return: the difference between start and stop
    """
    diff = np.diff(array)
    return [diff[:,i] for i in range(diff.shape[1])]


def remove_NAN(array):
    """
    remove the NAN from an array
    :param array: numpy array
    :return: array without NAN
    """
    return array[np.where(np.logical_not(np.isnan(array)))]


def get_data(path):
    """
    get the timer from a repository of simulation. Go on all the different localisation and file for timer
    :param path: path of the repository
    :return: dictionary with all the time
    """
    data = {}
    # get all the saving buffer of numpy except the init_spikes and init_rates because it's not need it
    for file_name_full in os.listdir(path):
        filename, file_extension = os.path.splitext(file_name_full)
        if file_extension == '.npy':
            if filename != 'init_spikes' and filename != 'init_rates':
                data[filename] = np.load(path+file_name_full)
    # get all special timer of nest same in txt file
    for file_name_full in os.listdir(path+'/nest/'):
        filename, file_extension = os.path.splitext(file_name_full)
        if file_extension == '.txt':
            if filename != 'spike_detector' and filename != 'spike_generator' :
                if filename == 'timer_0':
                    data_file = np.loadtxt(path+'/nest/'+file_name_full,dtype=np.str,delimiter=';')
                    data['nest_'+filename] = np.char.replace(data_file, ',', '.').astype(np.float)
                elif filename == 'timer_input_0':
                    data_file = np.loadtxt(path+'/nest/'+file_name_full,skiprows=1,dtype=np.str,delimiter=';')
                    data['nest_'+filename] = np.char.replace(data_file, ',', '.').astype(np.float)
                    data_file = np.loadtxt(path+'/nest/'+file_name_full,max_rows=1,dtype=np.str,delimiter=';')
                    data['nest_'+filename+'_init'] = np.char.replace(data_file, ',', '.').astype(np.float)
                elif  filename == 'timer_io_0':
                    data_file = np.loadtxt(path+'/nest/'+file_name_full,dtype=np.str,delimiter=';')
                    data['nest_'+filename] = np.char.replace(data_file, ',', '.').astype(np.float)
    return data


def analyse_tvb(tvb):
    """
    create the tree of simulation time for TVB
    :param tvb: tvb timer
    :return: tree of times
    """
    timer_value = get_time(tvb)
    tvb_node = Node('TVB',tvb[0,3]-tvb[0,0])
    init_tvb = Node('initialisation',timer_value[0,0])
    init_tvb.addNode('configure TVB',timer_value[1,0])
    end_tvb = Node('end',timer_value[0, 1])
    simulation_tvb = Node('simulation',tvb[0,2]-tvb[0,1])
    receive_tvb = Node('receive data',values=remove_NAN(timer_value[2,:]))
    simulation_tvb.add(receive_tvb)
    simulation_tvb.addNode('run simulation', values= remove_NAN(timer_value[3,:]))
    send_tvb = Node('send data',values= remove_NAN(timer_value[4,:]))
    simulation_tvb.add(send_tvb)
    send_tvb.addNode('wait send',values= remove_NAN(timer_value[5,:]))
    receive_tvb.addNode('wait receive',values=remove_NAN(timer_value[6,:]))
    tvb_node.adds(init_tvb,simulation_tvb,end_tvb)
    return tvb_node


def analyse_nest(nest,nest_init,nest_sim,nest_timer,nest_timer_input_init,nest_timer_input,wait_time,nest_timer_io):
    """
    create the tree of simulation time for Nest
    :param nest: time from python of Nest
    :param nest_init: time from initialisation timer
    :param nest_sim: time from simulation timer
    :param nest_timer: time from kernel of nest
    :param nest_timer_input_init: time form the initialisation of the input of nest
    :param nest_timer_input: time from the input of nest
    :param wait_time : time waiting by translator
    :param nest_timer_io: time from the io_manager of nest
    :return: tree of times
    """
    timer_value_nest = get_time(nest)
    timer_value_nest_init = get_time(nest_init)
    timer_value_nest_sim = remove_NAN(get_time(nest_sim))
    timer_value_nest_time = get_nest_time(nest_timer)
    timer_value_nest_time_input = get_nest_time(nest_timer_input)
    timer_value_nest_time_io = get_nest_time(nest_timer_io)

    nest_node = Node('Nest',nest[0,9]-nest[0,0])
    init_nest = Node('initialisation',nest[0,7]-nest[0,0])
    init_nest.addNode('start',timer_value_nest[0,0])
    init_config = Node('configuration',timer_value_nest[0,1])
    init_nest.add(init_config)
    init_nest.addNode('create file',timer_value_nest[0,2])
    init_nest.addNode('wait file port', timer_value_nest[0,3])
    simulation = Node('simulation', timer_value_nest[0,4])
    init_config.addNode('init kernel', timer_value_nest_init[0,0])
    init_config.addNode('init population_neurons', timer_value_nest_init[0,1])
    init_config.addNode('init connection',timer_value_nest_init[0,2])
    init_config.addNode('init device', timer_value_nest_init[0,3])
    prepare = Node('prepare',timer_value_nest_sim[0] )
    simulation.add( prepare )
    prepare.addNode('prepare input',nest_timer_input_init[1] - nest_timer_input_init[0])
    run_nest = Node('run', values=timer_value_nest_sim[2:-1])
    simulation.add(run_nest)
    pre_run = Node('pre-run', values=timer_value_nest_time[0] )
    run_nest.adds(pre_run)
    pre_run.addNode('pre_run_record',values = timer_value_nest_time_io[0])
    pre_run.addNode('pre_run_input',values = timer_value_nest_time_io[1])
    # wait_time = nest_timer_input[:,3]-nest_timer_input[:,0]
    pre_run.get('pre_run_input').addNode('pre_run_input_receive_data',values=timer_value_nest_time_input[0]-wait_time[np.logical_not(np.isnan(wait_time))] )
    pre_run.get('pre_run_input').addNode('pre_run_input_wait',values=wait_time[np.logical_not(np.isnan(wait_time))] )
    pre_run.get('pre_run_input').addNode('pre_run_input_update',values=timer_value_nest_time_input[1])
    run_nest.addNode('pre-run 2',values=timer_value_nest_time[1])
    run_nest.addNode('run simulation',values=timer_value_nest_time[2])
    run_nest.addNode('post-run',values=timer_value_nest_time[3])
    run_nest.get('post-run').addNode('post-run input',values=timer_value_nest_time_input[4])
    simulation.addNode('clean', timer_value_nest_sim[-1])
    nest_node.adds(init_nest,simulation)
    return nest_node


def analyse_translation_tvb_to_nest(index,master,send,receive):
    """
    create the tree of simulation time for translation TVB to Nest
    :param index: index of the translator
    :param master: from the master process of the translator
    :param send : time from the sending thread
    :param receive : time from the receiving thread
    :return: tree of times
    """
    time_value_master = get_time(master)
    time_value_send = get_time(send)
    time_value_receive = get_time(receive)
    translate = Node('Translation TVB to Nest '+str(index),master[0,9] - master[0,0],print_name='Translation<br>TVB to Nest '+str(index))
    initialisation = Node('initialisation', master[0,5]-master[0,0])
    initialisation.addNode('start',time_value_master[0,0])
    initialisation.addNode('MPI connection', time_value_master[0,1])
    initialisation.addNode('launch thread', time_value_master[0,2])
    simulation = Node('simulation', time_value_master[0,3])
    end = Node('Finalise', time_value_master[0,4])
    send_node = Node('send thread',send[0,3]-send[0,0])
    send_node.addNode('initialisation send thread', time_value_send[0,0])
    send_node.addNode('wait for sending message', values=remove_NAN(time_value_send[1,:]),print_name='wait for<br>sending<br>message')
    send_node.addNode('wait for receiving thread', values=remove_NAN(time_value_send[2,:]),print_name='wait for<br>receiving thread')
    send_node.addNode('copy buffer of spikes', values=remove_NAN(time_value_send[3,:]),print_name='copy buffer<br>of spikes')
    send_node.addNode('send data', values = remove_NAN(time_value_send[4,:]))
    send_node.addNode('end send thread', time_value_send[0,1])
    receive_node = Node('receive thread', receive[0,3]-receive[0,0])
    receive_node.addNode('initialisation thread receive', time_value_receive[0,0])
    receive_node.addNode('wait message', values=remove_NAN(time_value_receive[1,:]))
    receive_node.addNode('wait to send time', values= remove_NAN(time_value_receive[2,:]),print_name='wait<br>to send time')
    receive_node.addNode('receive data', values = remove_NAN(time_value_receive[3,:]))
    receive_node.addNode('generate data', values = remove_NAN(time_value_receive[4,:]))
    receive_node.addNode('wait sending thread', values = remove_NAN(time_value_receive[5,:]),print_name='wait<br>sending thread')
    receive_node.addNode('end receive thread', time_value_receive[0,1])
    simulation.adds(send_node,receive_node)
    translate.adds(initialisation,simulation,end)
    # for printing time
    translate.time *=2
    for i in translate.child:
        i.time *=2
    return translate


def analyse_translation_nest_to_tvb(index,master,send,receive):
    """
    create the tree of simulation time for translation Nest to TVB
    :param index: index of the translator
    :param master: from the master process of the translator
    :param send : time from the sending thread
    :param receive : time from the receiving thread
    :return: tree of times
    """
    time_value_master = get_time(master)
    time_value_send = get_time(send)
    time_value_receive = get_time(receive)
    translate = Node('Translation Nest to TVB '+str(index),master[0,9] - master[0,0],print_name='Translation<br>Nest to TVB '+str(index))
    initialisation = Node('initialisation', master[0,5]-master[0,0])
    initialisation.addNode('start',time_value_master[0,0])
    initialisation.addNode('connection MPI', time_value_master[0,1])
    initialisation.addNode('launch thread', time_value_master[0,2])
    simulation = Node('simulation', time_value_master[0,3]) # *2 for printing
    end = Node('Finalise', time_value_master[0,4])
    send_node = Node('send thread',send[0,3]-send[0,0])
    send_node.addNode('initialisation thread send', time_value_send[0,0])
    send_node.addNode('wait for sending message', values=remove_NAN(time_value_send[1,:]),print_name='wait for<br>sending<br>message')
    send_node.addNode('wait for receive thread', values=remove_NAN(time_value_send[2,:]),print_name='wait for<br>receive thread')
    send_node.addNode('generate data', values=remove_NAN(time_value_send[3,:]))
    send_node.addNode('send data', values = remove_NAN(time_value_send[4,:]))
    send_node.addNode('end send tread', time_value_send[0,1])
    receive_node = Node('receive thread', receive[0,3]-receive[0,0])
    receive_node.addNode('initialisation thread receive', time_value_receive[0,0])
    receive_node.addNode('start simulation message', values=remove_NAN(time_value_receive[1,:]))
    receive_node.addNode('wait for receiving message', values=remove_NAN(time_value_receive[2,:]),print_name='wait for<br>receiving<br>message')
    receive_node.addNode('receive data', values = remove_NAN(time_value_receive[3,:]))
    receive_node.addNode('wait the thread send', values = remove_NAN(time_value_receive[4,:]))
    receive_node.addNode('store data', values = remove_NAN(time_value_receive[5,:]))
    receive_node.addNode('end receive thread', time_value_receive[0,1])
    simulation.adds(send_node,receive_node)
    translate.adds(initialisation,simulation,end)
    # for printing time
    translate.time *=2
    for i in translate.child:
        i.time *=2
    return translate


def get_dictionnary(path):
    """
    function for getting the tree for all the simulation
    :param path: folder of the simulation
    :return: the tree of times and the index of the translator
    """
    # get data from path
    data = get_data(path)
    # get the id of translator
    pattern_nest_to_tvb = re.compile('nest_to_tvb_master*')
    index_translator_nest_to_tvb = []
    pattern_tvb_to_nest = re.compile('tvb_to_nest_master*')
    index_translator_tvb_to_nest = []
    for i in data.keys():
        if pattern_nest_to_tvb.match(i) is not None:
            index_translator_nest_to_tvb.append(pattern_nest_to_tvb.split(i)[1])
        if pattern_tvb_to_nest.match(i) is not None:
            index_translator_tvb_to_nest.append(pattern_tvb_to_nest.split(i)[1])

    # get the time of waiting data in the translator for nest
    wait_time_1 = get_time(data['tvb_to_nest_send'+str(index_translator_tvb_to_nest[0])])[2]
    wait_time_1 = wait_time_1[np.logical_not(np.isnan(wait_time_1))]
    wait_time_2 = get_time(data['tvb_to_nest_send'+str(index_translator_tvb_to_nest[1])])[2]
    wait_time_2 = wait_time_2[np.logical_not(np.isnan(wait_time_2))]
    if np.sum(wait_time_1) > np.sum(wait_time_2):
        wait_time = wait_time_1
    else:
        wait_time = wait_time_2

    #creation of the tree of times
    data_time = Node('root',0.0)
    data_time.add(analyse_tvb(data['timer_tvb']))
    data_time.add(analyse_nest(data['nest'],data['nest_init'],data['nest_sim'],data['nest_timer_0'],data['nest_timer_input_0_init'],data['nest_timer_input_0'],wait_time,data['nest_timer_io_0']))
    for index,i in enumerate(index_translator_nest_to_tvb):
        data_time.add(analyse_translation_nest_to_tvb(index,data['nest_to_tvb_master' + str(i)],
                                                         data['nest_to_tvb_send' + str(i)],
                                                         data['nest_to_tvb_receive' + str(i)]))
    for index,i in enumerate(index_translator_tvb_to_nest):
        data_time.add(analyse_translation_tvb_to_nest(index,data['tvb_to_nest_master'+str(i)],
                                                         data['tvb_to_nest_send'+str(i)],
                                                         data['tvb_to_nest_receive'+str(i)]))
    return data_time,(index_translator_nest_to_tvb,index_translator_tvb_to_nest)


if __name__ == '__main__':
    dict, index = get_dictionnary('./test_file/benchmark_paper_ebrains/0.1/10/1/1/0/_g_1.0_mean_I_ext_0.0/')
    print(index)
    print(dict)