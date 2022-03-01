#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
import os
import re


class Node:
    """
    The class for the structure of the tree
    """

    def __init__(self, name, time=0.0, values=None, print_name=None):
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

    def add(self, node):
        """
        add a child to the node
        :param node: the child node
        """
        self.child.append(node)

    def adds(self, *args):
        """
        adds multiple nodes
        :param args: list of node
        """
        for node in args:
            self.child.append(node)

    def addNode(self, *args, **kwargs):
        """
        create a node and add ti the list of child
        :param args: the argument for the node
        :param kwargs: the option for the node
        :return:
        """
        self.child.append(Node(*args, **kwargs))

    def get(self, name):
        """
        get a child by it's name
        :param name: name of the child
        :return:
        """
        for node in self.child:
            if node.name == name:
                return node

    def get_position(self, name):
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
                count += 1

    def to_array_for_print(self):
        """
        return an array for plotting or print it the tree ( recursive function)
        :return: values ( times of nodes), labels (name of the node), parents ( the parents node)
        """
        values = [self.time]
        labels = [self.print_name]
        parents = ['']
        for child in self.child:
            value_child, labels_child, parents_child = child.to_array_for_print()
            parents_child[0] = self.print_name
            values += value_child
            labels += labels_child
            parents += parents_child
        return values, labels, parents


def get_time(array):
    """
    return the time of the timer
    :param array: array of time start and stop
    :return: the difference between start and stop
    """
    if len(array.shape) == 1:
        return np.diff(array)[np.arange(0, array.shape[-1], 2)]
    if len(array.shape) == 2:
        return np.diff(array)[:, np.arange(0, array.shape[-1], 2)]


def get_nest_time(array):
    """
    same than previous for nest timer
    :param array: array of time start and stop
    :return: the difference between start and stop
    """
    diff = np.diff(array)
    return [diff[:, i] for i in range(diff.shape[1])]


def get_nest_time_input(array):
    """
    same than previous for nest timer input
    :param array: array of time start and stop
    :return: the difference between start and stop
    """
    res = np.empty((array.shape[0], 4))
    res[:, 0] = array[:, 2] - array[:, 0]  # pre run
    res[:, 1] = array[:, 1] - array[:, 0]  # wait first data
    res[:, 2] = array[:, 3] - array[:, 1]  # receive data
    res[:, 3] = array[:, 5] - array[:, 4]  # post run
    return res.T


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
                data[filename] = np.load(path + file_name_full)
    # get all special timer of nest same in txt file
    for file_name_full in os.listdir(path + '/nest/'):
        filename, file_extension = os.path.splitext(file_name_full)
        if file_extension == '.txt':
            if filename != 'spike_detector' and filename != 'spike_generator':
                if filename == 'timer_0':
                    data_file = np.loadtxt(path + '/nest/' + file_name_full, dtype=str, delimiter=';')
                    data['nest_' + filename] = np.char.replace(data_file, ',', '.').astype(float)
                elif filename == 'timer_input_0':
                    data_file = np.loadtxt(path + '/nest/' + file_name_full, skiprows=1, dtype=str, delimiter=';')
                    data['nest_' + filename] = np.char.replace(data_file, ',', '.').astype(float)
                    data_file = np.loadtxt(path + '/nest/' + file_name_full, max_rows=1, dtype=str, delimiter=';')
                    data['nest_' + filename + '_init'] = np.char.replace(data_file, ',', '.').astype(float)
                elif filename == 'timer_io_0':
                    data_file = np.loadtxt(path + '/nest/' + file_name_full, dtype=str, delimiter=';')
                    data['nest_' + filename] = np.char.replace(data_file, ',', '.').astype(float)
    return data


def analyse_tvb(tvb, wait_time):
    """
    create the tree of simulation time for TVB
    :param tvb: tvb timer
    :return: tree of times
    """
    timer_value = get_time(tvb)
    tvb_node = Node('TVB', tvb[0, 9] - tvb[0, 0])
    init_tvb = Node('initialisation', tvb[0, 7] - tvb[0, 0])
    init_tvb.addNode('configure TVB', timer_value[0, 1])
    init_tvb.addNode('send initialisation TVB', timer_value[0, 3])
    end_tvb = Node('end', timer_value[0, 4])
    simulation_tvb = Node('simulation', tvb[0, 8] - tvb[0, 7])
    receive_tvb = Node('receive data', values=remove_NAN(timer_value[1, :]))
    simulation_tvb.add(receive_tvb)
    simulation_tvb.addNode('run simulation', values=remove_NAN(timer_value[2, :]))
    send_tvb = Node('send data', values=remove_NAN(timer_value[3, :]))
    simulation_tvb.add(send_tvb)
    send_tvb.addNode('wait check', values=remove_NAN(timer_value[4, :]))
    receive_time = Node('receive time', values=remove_NAN(timer_value[5, :]))
    receive_tvb.add(receive_time)
    receive_time.addNode('wait receive', values=wait_time[np.logical_not(np.isnan(wait_time))])
    tvb_node.adds(init_tvb, simulation_tvb, end_tvb)
    return tvb_node


def analyse_nest(nest, nest_init, nest_sim, nest_timer, nest_timer_input_init, nest_timer_input, wait_time,
                 nest_timer_io):
    """
    create the tree of simulation time for NEST
    :param nest: time from python of NEST
    :param nest_init: time from initialisation timer
    :param nest_sim: time from simulation timer
    :param nest_timer: time from kernel of nest
    :param nest_timer_input_init: time form the initialisation of the input of nest
    :param nest_timer_input: time from the input of nest
    :param wait_time : time waiting by transformer
    :param nest_timer_io: time from the io_manager of nest
    :return: tree of times
    """
    timer_value_nest = get_time(nest)
    timer_value_nest_init = get_time(nest_init)
    timer_value_nest_sim = remove_NAN(get_time(nest_sim))
    timer_value_nest_time = get_nest_time(nest_timer)
    timer_value_nest_time_input = get_nest_time_input(nest_timer_input)
    timer_value_nest_time_io = get_nest_time(nest_timer_io)

    nest_node = Node('NEST', nest[0, 9] - nest[0, 0])
    init_nest = Node('initialisation', nest[0, 7] - nest[0, 0])
    init_nest.addNode('start', timer_value_nest[0, 0])
    init_config = Node('configuration', timer_value_nest[0, 1])
    init_nest.add(init_config)
    init_nest.addNode('create file', timer_value_nest[0, 2])
    init_nest.addNode('wait file port', timer_value_nest[0, 3])
    simulation = Node('simulation nest', timer_value_nest[0, 4])
    init_config.addNode('init kernel', timer_value_nest_init[0, 0])
    init_config.addNode('init population_neurons', timer_value_nest_init[0, 1])
    init_config.addNode('init connection', timer_value_nest_init[0, 2])
    init_config.addNode('init device', timer_value_nest_init[0, 3])
    prepare = Node('prepare', timer_value_nest_sim[0])
    simulation.add(prepare)
    prepare.addNode('prepare input', nest_timer_input_init[1] - nest_timer_input_init[0])
    run_nest = Node('run', values=timer_value_nest_sim[2:-1])
    simulation.add(run_nest)
    pre_run = Node('pre-run', values=timer_value_nest_time[0])
    run_nest.adds(pre_run)
    run_nest.addNode('pre-run_2', values=timer_value_nest_time[1])
    pre_run.addNode('pre_run_record', values=timer_value_nest_time_io[0])
    pre_run.addNode('pre_run_input', values=timer_value_nest_time_io[1])
    # wait_time = nest_timer_input[:,3]-nest_timer_input[:,0]
    pre_run.get('pre_run_input').addNode('pre_run_input_receive_data',
                                         values=timer_value_nest_time_input[0] - wait_time[
                                             np.logical_not(np.isnan(wait_time))])
    pre_run.get('pre_run_input').addNode('pre_run_input_wait', values=wait_time[np.logical_not(np.isnan(wait_time))])
    # pre_run.get('pre_run_input').addNode('pre_run_update', values=timer_value_nest_time_input[0]) # not precise
    # pre_run.get('pre_run_input').get('pre_run_update').addNode('pre-run wait send first',         # not precise
    #                                                            values=timer_value_nest_time_input[1])
    pre_run.get('pre_run_input').get('pre_run_input_receive_data').addNode('send message',
                                                                           values=timer_value_nest_time_input[2])
    run_nest.addNode('simulation kernel nest', values=timer_value_nest_time[2])
    run_nest.addNode('post-run', values=timer_value_nest_time[3])
    run_nest.get('post-run').addNode('post-run input', values=timer_value_nest_time_input[3])
    simulation.addNode('clean', timer_value_nest_sim[-1])
    nest_node.adds(init_nest, simulation)
    return nest_node


def init_transformation(master, data, name_root, create_connection=True):
    """
    create the tree of simulation time for transformation TVB to NEST
    :param master: time of the main program
    :param name_root: name of root
    :param data: time of each process/thread
    :param create_connection: creation or not of the MPI connection with simulator
    :return: tree of times
    """
    time_value_master = get_time(master)
    time_value_io_mpi_ext = get_time(data[0])
    tree = Node(name_root, master[0, 9] - master[0, 0])
    initialisation = Node('initialisation', master[0, 6] - master[0, 0])
    initialisation.addNode('start', time_value_master[0, 0])
    initialisation.addNode('wait file with id of nest devices', time_value_master[0, 1])
    initialisation.addNode('prepare for launch process', time_value_master[0, 2])
    if create_connection:
        initialisation.time += time_value_io_mpi_ext[0] + time_value_io_mpi_ext[1]
        initialisation.addNode('create connection', time_value_io_mpi_ext[0])
        initialisation.addNode('wait connection', time_value_io_mpi_ext[1])
        # simulation = Node('simulation', time_value_io_mpi_ext[2] # finer timer of simulation
        simulation = Node('simulation', time_value_master[0, 3]
                          - (time_value_io_mpi_ext[3] + time_value_io_mpi_ext[4] + time_value_io_mpi_ext[0] +
                             time_value_io_mpi_ext[1]))
        end = Node('Finalise', time_value_master[0, 4] + time_value_io_mpi_ext[3] + time_value_io_mpi_ext[4])
        end.addNode('close connection MPI', time_value_io_mpi_ext[3])
        end.addNode('finalise MPI', time_value_io_mpi_ext[4])
    else:
        initialisation.time += time_value_io_mpi_ext[0]
        initialisation.addNode('create connection', time_value_io_mpi_ext[0])
        # simulation = Node('simulation', time_value_io_mpi_ext[1] # finer timer of simulation
        simulation = Node('simulation', time_value_master[0, 3]
                          - (time_value_io_mpi_ext[0] + time_value_io_mpi_ext[2] + time_value_io_mpi_ext[3]))
        end = Node('Finalise', time_value_master[0, 4] + time_value_io_mpi_ext[2] + time_value_io_mpi_ext[3])
        end.addNode('close connection MPI', time_value_io_mpi_ext[2])
        end.addNode('finalise MPI', time_value_io_mpi_ext[3])

    tree.adds(initialisation, simulation, end)
    return tree


def add_prefix(tree, prefix):
    """
    add the prefix of transformer for
    :param tree: tree of timer
    :param prefix: prefix to add to all names
    :return:
    """
    tree.print_name = prefix + tree.print_name
    tree.name = prefix + tree.name
    for child in tree.child:
        add_prefix(child, prefix)


def analyse_tvb_to_nest_sender(index, master, data_send, mpi):
    """
    create the tree of simulation time for transformation TVB to NEST
    producer of data in nest
    :param index: index of the transformer
    :param master: from the master process of the transformer
    :param data_send : timer of process or thread
    :param mpi: mpi for internal communication
    :return: tree of times
    """
    time_value_send = get_time(data_send)
    name = 'TVB_NEST_' + str(index) + ': Producer NEST data '
    transform = init_transformation(master, data_send, name)

    sim_process = transform.get('simulation')
    sim_process.addNode('receive spikes', values=remove_NAN(time_value_send[1, :]))
    sim_process.addNode('receive end run', values=remove_NAN(time_value_send[2, :]))
    sim_process.addNode('get internal spikes', values=remove_NAN(time_value_send[3, :]))
    sim_process.addNode('send spikes', values=remove_NAN(time_value_send[4, :]))
    sim_process.addNode('end writing', values=remove_NAN(time_value_send[5, :]))

    if mpi:
        sim_process.get('get internal spikes').addNode("receive size", values=remove_NAN(time_value_send[10, :]))
        sim_process.get('get internal spikes').addNode("wait read buffer", values=remove_NAN(time_value_send[11, :]))
        sim_process.get('send spikes').addNode("reshape buffer", values=remove_NAN(time_value_send[6, :]))
        sim_process.addNode("release buffer", remove_NAN(time_value_send[12, :]))
    else:
        sim_process.get('get internal spikes').addNode("wait read buffer", values=remove_NAN(time_value_send[11, :]),
                                                       print_name="wait<br>write buffer")
        sim_process.get('get internal spikes').addNode("end read buffer", values=remove_NAN(time_value_send[12, :]))
        sim_process.get('send spikes').addNode("reshape read buffer", values=remove_NAN(time_value_send[6, :]))
        sim_process.addNode("release read buffer", values=remove_NAN(time_value_send[13, :]))

    return transform


def analyse_tvb_to_nest_receiver(index, master, data_receive, mpi):
    """
    create the tree of simulation time for transformation TVB to NEST
    Consumer TVB data
    :param index: index of the transformer
    :param master: from the master process of the transformer
    :param data_receive : timer of process or thread
    :param mpi: mpi for internal communication
    :return: tree of times
    """
    time_value_receive = get_time(data_receive)
    name = 'TVB_NEST_' + str(index) + ': Consumer TVB data '
    transform = init_transformation(master, data_receive, name)

    sim_process = transform.get('simulation')
    sim_process.addNode('send check', values=remove_NAN(time_value_receive[1, :]))
    sim_process.addNode('receive time', values=remove_NAN(time_value_receive[2, :]))
    sim_process.addNode('get rate', values=remove_NAN(time_value_receive[3, :]))
    sim_process.addNode('transfer end', values=remove_NAN(time_value_receive[4, :]))

    if mpi:
        sim_process.get('transfer end').addNode("release read buffer", values=remove_NAN(time_value_receive[17, :]))
    else:
        sim_process.get('get rate').addNode("wait write buffer", values=remove_NAN(time_value_receive[8, :]),
                                            print_name="wait<br>write buffer")
        sim_process.get('get rate').addNode("end write buffer", values=remove_NAN(time_value_receive[9, :]))
        sim_process.addNode("release write buffer", values=remove_NAN(time_value_receive[10, :]))

    return transform


def analyse_tvb_to_nest_transformer(index, master, data_transform, mpi):
    """
    create the tree of simulation time for transformation TVB to NEST
    transformer function
    :param index: index of the transformer
    :param master: from the master process of the transformer
    :param data_transform: timer of process or thread
    :param mpi: mpi for internal communication
    :return: tree of times
    """
    time_value_transformer = get_time(data_transform)
    name = 'TVB_NEST_' + str(index) + ': Transformer function '
    transform = init_transformation(master, data_transform, name, create_connection=False)

    sim_process = transform.get('simulation')
    sim_process.addNode('get rate', values=remove_NAN(time_value_transformer[1, :]))
    sim_process.addNode('release rate', values=remove_NAN(time_value_transformer[2, :]))
    sim_process.addNode('save rate', values=remove_NAN(time_value_transformer[3, :]))
    sim_process.addNode('generate spikes', values=remove_NAN(time_value_transformer[4, :]))
    sim_process.addNode('save spikes', values=remove_NAN(time_value_transformer[5, :]))
    sim_process.addNode('send spike trains', values=remove_NAN(time_value_transformer[6, :]))
    sim_process.addNode('end connection', values=remove_NAN(time_value_transformer[7, :]))

    if mpi:
        sim_process.get('send spike trains').addNode("send size", values=remove_NAN(time_value_transformer[8, :]))
        sim_process.get('send spike trains').addNode("reshape data", values=remove_NAN(time_value_transformer[13, :]))
        sim_process.get('end connection').addNode("release read buffer",
                                                  values=remove_NAN(time_value_transformer[18, :]))
        sim_process.get('end connection').time -= 0.04
        sim_process.get('end connection').get("release read buffer").time -= 0.04
        sim_process.get('get rate').addNode("receive time", values=remove_NAN(time_value_transformer[15, :]))
        sim_process.get('get rate').addNode("receive rate", values=remove_NAN(time_value_transformer[16, :]))
    else:
        sim_process.get('send spike trains').addNode("wait write buffer",
                                                     values=remove_NAN(time_value_transformer[8, :]),
                                                     print_name="wait<br>write buffer")
        sim_process.get('send spike trains').addNode("reshape data", values=remove_NAN(time_value_transformer[14, :]))
        sim_process.get('send spike trains').addNode("end write", values=remove_NAN(time_value_transformer[9, :]))
        sim_process.get('end connection').addNode("release write buffer",
                                                  values=remove_NAN(time_value_transformer[10, :]))
        sim_process.get('get rate').addNode("wait read buffer", values=remove_NAN(time_value_transformer[11, :]))
        sim_process.get('get rate').addNode("end read", values=remove_NAN(time_value_transformer[12, :]))
        sim_process.get('end connection').addNode("release read buffer",
                                                  values=remove_NAN(time_value_transformer[13, :]))

    return transform


def analyse_nest_to_tvb_send(index, master, data_sender, mpi):
    """
    create the tree of simulation time for transformation NEST to TVB
    Producer TVB data
    :param index: index of the transformer
    :param master: from the master process of the transformer
    :param data_sender: timer of process or thread
    :param mpi: mpi for internal communication
    :return: tree of times
    """
    time_value_sender = get_time(data_sender)
    name = 'NEST_TVB_' + str(index) + ': Producer TVB data '
    transform = init_transformation(master, data_sender, name)

    sim_process = transform.get('simulation')
    sim_process.addNode('receive check', values=remove_NAN(time_value_sender[1, :]))
    sim_process.addNode('get rate and time', values=remove_NAN(time_value_sender[2, :]))
    sim_process.addNode('send rate and time', values=remove_NAN(time_value_sender[3, :]))
    sim_process.addNode('release buffer', values=remove_NAN(time_value_sender[4, :]))

    if mpi:
        sim_process.get('get rate and time').addNode("get time", values=remove_NAN(time_value_sender[15, :]))
        sim_process.get('get rate and time').addNode("get rate", values=remove_NAN(time_value_sender[16, :]))
    else:
        sim_process.get('get rate and time').addNode("wait read buffer", values=remove_NAN(time_value_sender[11, :]))
        sim_process.get('release buffer').addNode("end read buffer", values=remove_NAN(time_value_sender[12, :]))
        sim_process.addNode("release read buffer", values=remove_NAN(time_value_sender[13, :]))
    return transform


def analyse_nest_to_tvb_receive(index, master, data_receive, mpi):
    """
    create the tree of simulation time for transformation NEST to TVB
    Consumer nest data
    :param index: index of the transformer
    :param master: from the master process of the transformer
    :param data_receive: timer of process or thread
    :param mpi: mpi for internal communication
    :return: tree of times
    """
    time_value_receive = get_time(data_receive)
    name = 'NEST_TVB_' + str(index) + ': Consumer NEST data '
    transform = init_transformation(master, data_receive, name)

    sim_process = transform.get('simulation')
    sim_process.addNode('receive spikes', values=remove_NAN(time_value_receive[1, :]))
    sim_process.addNode('receive end run', values=remove_NAN(time_value_receive[2, :]))
    sim_process.addNode('buffer ready', values=remove_NAN(time_value_receive[3, :]))
    sim_process.addNode('wait the first message', values=remove_NAN(time_value_receive[4, :]))
    sim_process.addNode('get spikes', values=remove_NAN(time_value_receive[5, :]))
    sim_process.addNode('send internal spike', values=remove_NAN(time_value_receive[6, :]))

    if mpi:
        sim_process.get('send internal spike').addNode("send size", values=remove_NAN(time_value_receive[8, :]))
        sim_process.addNode("release write buffer", remove_NAN(time_value_receive[9, :]))
    else:
        sim_process.get('buffer ready').addNode("wait write buffer", values=remove_NAN(time_value_receive[8, :]),
                                                print_name="wait<br>write buffer")
        sim_process.get('send internal spike').addNode("end write buffer", values=remove_NAN(time_value_receive[9, :]))
        sim_process.addNode("release write buffer", values=remove_NAN(time_value_receive[10, :]))

    return transform


def analyse_nest_to_tvb_transfomer(index, master, data_transformer, mpi):
    """
    create the tree of simulation time for transformation NEST to TVB
    function for transformer
    :param index: index of the transformer
    :param master: from the master process of the transformer
    :param data_transformer: timer of process or thread
    :param mpi: mpi for internal communication
    :return: tree of times
    """
    time_value_transformer = get_time(data_transformer)
    name = 'NEST_TVB_' + str(index) + ': Transformer function '
    transform = init_transformation(master, data_transformer, name, create_connection=False)

    sim_process = transform.get('simulation')
    sim_process.addNode('ready to get data', values=remove_NAN(time_value_transformer[1, :]))
    sim_process.addNode('create histogram', values=remove_NAN(time_value_transformer[2, :]))
    sim_process.addNode('release buffer', values=remove_NAN(time_value_transformer[3, :]))
    sim_process.addNode('save_hist', values=remove_NAN(time_value_transformer[4, :]))
    sim_process.addNode('analyse', values=remove_NAN(time_value_transformer[5, :]))
    sim_process.addNode('save_rate', values=remove_NAN(time_value_transformer[6, :]))
    sim_process.addNode('send rates', values=remove_NAN(time_value_transformer[7, :]))

    if mpi:
        sim_process.get('ready to get data').addNode("receive size", values=remove_NAN(time_value_transformer[10, :]))
        sim_process.get('ready to get data').addNode("wait buffer", values=remove_NAN(time_value_transformer[11, :]))
        sim_process.get('send rates').addNode("send rate", values=remove_NAN(time_value_transformer[17, :]))
    else:
        sim_process.get('ready to get data').addNode("wait read buffer",
                                                     values=remove_NAN(time_value_transformer[11, :]))
        sim_process.get('ready to get data').addNode("end read buffer",
                                                     values=remove_NAN(time_value_transformer[12, :]))
        sim_process.get('release buffer').addNode("release read buffer",
                                                  values=remove_NAN(time_value_transformer[13, :]))
        sim_process.get('send rates').addNode("wait write buffer", values=remove_NAN(time_value_transformer[8, :]))
        sim_process.get('send rates').addNode("end write buffer", values=remove_NAN(time_value_transformer[9, :]))
        sim_process.get('send rates').addNode("release write buffer", values=remove_NAN(time_value_transformer[10, :]))

    return transform


def get_dictionnary(path, mpi, transformation=True):
    """
    function for getting the tree for all the simulation
    :param path: folder of the simulation
    :return: the tree of times and the index of the transformer
    """
    # get data from path
    data = get_data(path)

    if transformation:
        # get the id of transformer
        pattern_nest_to_tvb = re.compile('timer_nest_to_tvb_send*')
        index_transformer_nest_to_tvb = []
        pattern_tvb_to_nest = re.compile('timer_tvb_to_nest_sender*')
        index_transformer_tvb_to_nest = []
        for i in data.keys():
            if pattern_nest_to_tvb.match(i) is not None:
                index_transformer_nest_to_tvb.append(int(pattern_nest_to_tvb.split(i)[1]))
            if pattern_tvb_to_nest.match(i) is not None:
                index_transformer_tvb_to_nest.append(int(pattern_tvb_to_nest.split(i)[1]))
        index_transformer_nest_to_tvb = np.sort(index_transformer_nest_to_tvb)
        index_transformer_tvb_to_nest = np.sort(index_transformer_tvb_to_nest)

        # get the time of waiting data in the transformer for TVB
        wait_time_nest = np.zeros((500,))
        index_wait = 10 if mpi else 11
        for index in index_transformer_tvb_to_nest:
            wait_time = get_time(data['timer_tvb_to_nest_sender' + str(index)])[index_wait]
            wait_time = wait_time[np.logical_not(np.isnan(wait_time))]
            if np.sum(wait_time) > np.sum(wait_time_nest):
                wait_time_nest = wait_time

        # get the time of waiting data in the transformer for TVB
        wait_time_tvb = np.zeros((500,))
        index_wait = 15 if mpi else 11
        for index in index_transformer_nest_to_tvb:
            wait_time = get_time(data['timer_nest_to_tvb_send' + str(index)])[index_wait]
            wait_time = wait_time[np.logical_not(np.isnan(wait_time))]
            if np.sum(wait_time) > np.sum(wait_time_tvb):
                wait_time_tvb = wait_time
    else:
        wait_time_tvb = np.zeros((500,))
        wait_time_nest = np.zeros((500,))

    # creation of the tree of times
    data_time = Node('root', 0.0)
    data_time.add(analyse_tvb(data['timer_tvb'], wait_time_tvb))
    data_time.add(
        analyse_nest(data['timer_nest'], data['timer_nest_init'], data['timer_nest_sim'], data['nest_timer_0'],
                     data['nest_timer_input_0_init'], data['nest_timer_input_0'], wait_time_nest,
                     data['nest_timer_io_0']))
    if transformation:
        for index, i in enumerate(index_transformer_nest_to_tvb):
            data_time.add(analyse_nest_to_tvb_send(index, data['timer_nest_to_tvb_' + str(index)],
                                                   data['timer_nest_to_tvb_send' + str(i)], mpi))
            data_time.add(analyse_nest_to_tvb_transfomer(index, data['timer_nest_to_tvb_' + str(index)],
                                                         data['timer_nest_to_tvb_transformer' + str(i)], mpi))
            data_time.add(analyse_nest_to_tvb_receive(index, data['timer_nest_to_tvb_' + str(index)],
                                                      data['timer_nest_to_tvb_receive' + str(i)], mpi))
        for index, i in enumerate(index_transformer_tvb_to_nest):
            data_time.add(analyse_tvb_to_nest_sender(index, data['timer_tvb_to_nest_' + str(index)],
                                                     data['timer_tvb_to_nest_sender' + str(i)], mpi))
            data_time.add(analyse_tvb_to_nest_transformer(index, data['timer_tvb_to_nest_' + str(index)],
                                                          data['timer_tvb_to_nest_transformer' + str(i)], mpi))
            data_time.add(analyse_tvb_to_nest_receiver(index, data['timer_tvb_to_nest_' + str(index)],
                                                       data['timer_tvb_to_nest_receiver' + str(i)], mpi))
        return data_time, (index_transformer_nest_to_tvb, index_transformer_tvb_to_nest)
    else:
        return data_time


if __name__ == '__main__':
    import os

    path_global = os.path.dirname(os.path.realpath(__file__))
    tree, indexes = get_dictionnary(path_global + '/../../data/timer/paper_time_thread/1/0/_g_10.0_mean_I_ext_0.0/', False)
    # tree, indexes = get_dictionnary(path_global + '/../../data/timer/paper_mpi/1/0/_g_10.0_mean_I_ext_0.0/', True)
    print(indexes)
    print(tree)
