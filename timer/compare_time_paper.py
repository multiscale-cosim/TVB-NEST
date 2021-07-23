#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
import numpy as np


def full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait, time_TR_1_wait, time_TR_2_wait,
                time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                title,
                function=np.mean,
                log_option=False,
                ylabel_1='Wall time of the simulation in s',
                ylabel_2='Stack of percentage of\nsimulated time',
                ylabel_3='Percentage of\nsimulated time'
                ):
    """
    create figure for comparison time of multiple configuration
    :param list_nb: list of increment of x axis
    :param time_sim: time of simulation
    :param time_nest_sim: time of nest simulation
    :param time_nest_IO: time of communication of nest
    :param time_nest_wait: time of waiting data by nest
    :param time_TR_1_wait: time of translation wait
    :param time_TR_2_wait: time of translation wait
    :param time_nest_tot: total time of Nest simulation
    :param time_TVB_sim: time of simulation of TVB
    :param time_TVB_IO: time of communication of TVB
    :param time_TVB_tot: total time of TVB simulation
    :param title: title of graph
    :param function: function for grouping trial
    :param log_option: logarithm scale of x axis
    :param ylabel_1: y label 1
    :param ylabel_2: y label 2
    :param ylabel_3: y label 3
    :return: figure
    """
    # plot the result
    fig = plt.figure(figsize=(20, 20))

    # print time
    plt.subplot(121)
    ax = plt.gca()
    ax.fill_between(list_nb,
                    (function(time_TVB_sim, axis=1) + function(time_TVB_IO, axis=1)),
                    function(time_sim, axis=1),
                    color='y', label='co-simulation', alpha=0.2)
    ax.fill_between(list_nb,
                    np.zeros_like(function(time_nest_sim, axis=1)),
                    (function(time_nest_sim, axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='Nest simulation', alpha=0.5, hatch='o')
    ax.fill_between(list_nb,
                    (function(time_nest_sim, axis=1)),
                    (function(time_nest_IO, axis=1) + function(time_nest_sim, axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='Nest IO', alpha=0.5, hatch='oo')
    ax.fill_between(list_nb,
                    (function(time_nest_IO, axis=1) + function(time_nest_sim, axis=1)),
                    (function(time_nest_wait, axis=1) + function(time_nest_IO, axis=1) + function(time_nest_sim,
                                                                                                  axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='Wait to data for Nest', alpha=0.5, hatch='.')
    ax.fill_between(list_nb,
                    np.zeros_like(function(time_TVB_sim, axis=1)),
                    (function(time_TVB_sim, axis=1)),
                    color=[71 / 255, 164 / 255, 226 / 255], label='TVB simulation', alpha=1.0, facecolor="none",
                    hatch='|')
    ax.fill_between(list_nb,
                    (function(time_TVB_sim, axis=1)),
                    (function(time_TVB_sim, axis=1) + function(time_TVB_IO, axis=1)),
                    color=[71 / 255, 164 / 255, 226 / 255], label='TVB IO', alpha=1.0, hatch='\\', facecolor="none")
    plt.ylim(ymin=0.0)
    if log_option:
        plt.xscale('log')
    plt.legend(fontsize=15, loc=2)
    plt.tick_params(axis='both', labelsize=20)
    ax.set_ylabel(ylabel_1, fontsize=20)

    # print percentage cumulative
    plt.subplot(222)
    print("plot")
    plt.plot(list_nb,
             (function(time_nest_sim, axis=1) + function(time_nest_IO, axis=1)) / function(time_sim, axis=1) * 100, '-',
             color=[255 / 255, 104 / 255, 65 / 255], label='Nest simulation')
    plt.plot(list_nb, (function(time_nest_IO, axis=1)) / function(time_sim, axis=1) * 100, '--',
             color=[255 / 255, 104 / 255, 65 / 255], label='Nest IO')
    plt.plot(list_nb, (function(time_nest_wait, axis=1) + function(time_nest_IO, axis=1) + function(time_nest_sim,
                                                                                                    axis=1)) / function(
        time_sim, axis=1) * 100, '-.',
             color=[255 / 255, 104 / 255, 65 / 255], label='Wait to data for Nest')
    plt.plot(list_nb,
             (function(time_TVB_IO, axis=1) + function(time_TVB_sim, axis=1)) / function(time_sim, axis=1) * 100,
             '-',
             color=[71 / 255, 164 / 255, 226 / 255], label='TVB simulation')
    plt.plot(list_nb, (function(time_TVB_IO, axis=1)) / function(time_sim, axis=1) * 100, '--',
             color=[71 / 255, 164 / 255, 226 / 255], label='TVB IO')
    plt.plot(list_nb, function(time_sim, axis=1) / function(time_sim, axis=1) * 100,
             'y-', label='co-simulation')
    plt.ylim(ymin=0.0)
    if log_option:
        plt.xscale('log')
    plt.tick_params(axis='both', labelsize=20)
    plt.legend(fontsize=15)
    plt.ylabel(ylabel_2, fontsize=20, labelpad=-12)

    # print percentage
    plt.subplot(224)
    plt.plot(list_nb, (function(time_nest_IO, axis=1)) / function(time_sim, axis=1) * 100, '--',
             color=[255 / 255, 104 / 255, 65 / 255], label='Nest IO')
    plt.plot(list_nb, (function(time_nest_wait, axis=1)) / function(time_sim, axis=1) * 100, '-.',
             color=[255 / 255, 104 / 255, 65 / 255], label='Wait to data for Nest')
    plt.plot(list_nb, (function(time_nest_sim, axis=1)) / function(time_sim, axis=1) * 100, '-',
             color=[255 / 255, 104 / 255, 65 / 255], label='Nest simulation')
    plt.plot(list_nb, function(time_sim, axis=1) / function(time_sim, axis=1) * 100,
             'y-', label='co-simulation')
    plt.ylim(ymin=0.0)
    if log_option:
        plt.xscale('log')
    plt.legend(fontsize=15)
    plt.tick_params(axis='both', labelsize=20)
    plt.ylabel(ylabel_3, fontsize=20, labelpad=-12)

    # add labels and some configuration
    fig.text(0.5, 0.04, title, ha='center', va='center', fontsize=20)


# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    folders_list = [
        ('./test_file/paper_nb_neurons/',
         np.array(np.around(np.logspace(1,5,30)),dtype=int),
         'number of neurons simulated with Nest'),
        # ('./test_file/paper_mpi/', np.arange(1, 13, 1),
        #  'number of MPI using by Nest ( 1 MPI = 1 VP)'),
        ('./test_file/paper_time_thread/', np.arange(1, 13, 1),
         'number of virtual process of Nest (number of MPI : 1)'),
        # ('./test_file/paper_mpi_vp_2/', np.arange(2, 13, 2),
        #  'number of virtual process of Nest (number of MPI : 2)'),
        # ('./test_file/paper_mpi_vp_4/', np.arange(4, 13, 4),
        #  'number of virtual process of Nest (number of MPI : 4)'),
        ('./test_file/paper_time_synch/', [0.1, 0.2, 0.4, 0.5, 0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.6, 1.7, 1.8, 2.0, 2.1],
         'time of synchronization between Nest and TVB (in ms)'),
    ]  # same data for the three case
    mpi = False
    folders = [[] for i in folders_list]  # same data for the three case
    data = [[] for i in folders_list]  # same data for the three case
    nb_trial = 10  # the number of trial
    for index, (folder, list_nb, label) in enumerate(folders_list):
        for nb in list_nb:
            # the three test
            folders[index].append(folder + str(nb))
    for index_run, ((folder, list_nb, label), folder) in enumerate(zip(folders_list, folders)):
        data[index_run] = {'nest_sim': None,
                           'nest_IO': None,
                           'tvb_sim': None,
                           'sim': None,
                           }
        # get data
        time_sim = []
        time_nest_sim = []
        time_nest_IO = []
        time_nest_wait = []
        time_TR_1_wait = []
        time_TR_2_wait = []
        time_nest_tot = []
        time_TVB_sim = []
        time_TVB_IO = []
        time_TVB_tot = []
        for index_folder, name_folder in enumerate(folder):
            time_sim.append([])
            time_nest_sim.append([])
            time_nest_IO.append([])
            time_nest_wait.append([])
            time_TR_1_wait.append([])
            time_TR_2_wait.append([])
            time_nest_tot.append([])
            time_TVB_sim.append([])
            time_TVB_IO.append([])
            time_TVB_tot.append([])
            for trial in range(nb_trial):
                print(name_folder + '/' + str(trial) + '/_g_10.0_mean_I_ext_0.0/')
                tree, index = get_dictionnary(name_folder + '/' + str(trial) + '/_g_10.0_mean_I_ext_0.0/', mpi=mpi)
                time_sim[index_folder].append(tree.get('Nest').time)
                time_nest_sim[index_folder].append(
                    tree.get('Nest').get('simulation nest').get('run').get('simulation kernel nest').time)
                time_nest_IO[index_folder].append(
                    tree.get('Nest').get('simulation nest').get('run').get('pre-run').time
                    - tree.get('Nest').get('simulation nest').get('run').get('pre-run').get(
                        'pre_run_input').get('pre_run_input_wait').time
                    + tree.get('Nest').get('simulation nest').get('run').get('post-run').time)
                time_nest_wait[index_folder].append(
                    tree.get('Nest').get('simulation nest').get('run').get('pre-run').get(
                        'pre_run_input').get('pre_run_input_wait').time)
                time_TR_1_wait[index_folder].append(
                    tree.get('TVB_NEST_0: Producer Nest data ').get('simulation').get('get internal spikes').get(
                        'wait read buffer').time)
                time_TR_2_wait[index_folder].append(
                    tree.get('TVB_NEST_1: Producer Nest data ').get('simulation').get('get internal spikes').get(
                        'wait read buffer').time)
                time_nest_tot[index_folder].append(
                    tree.get('Nest').get('simulation nest').get('run').get('simulation kernel nest').time
                    + tree.get('Nest').get('simulation nest').get('run').get('pre-run').get('pre_run_input').time
                    + tree.get('Nest').get('simulation nest').get('run').get('post-run').time)
                time_TVB_sim[index_folder].append(
                    tree.get('TVB').get('simulation').get('run simulation').time)
                time_TVB_IO[index_folder].append(
                    tree.get('TVB').get('simulation').get('receive data').time
                    - tree.get('TVB').get('simulation').get('receive data').get('receive time').time
                    + tree.get('TVB').get('simulation').get('send data').time
                )
                time_TVB_tot[index_folder].append(
                    tree.get('TVB').get('simulation').get('run simulation').time
                    + tree.get('TVB').get('simulation').get('receive data').time
                    - tree.get('TVB').get('simulation').get('receive data').get('receive time').time
                    + tree.get('TVB').get('simulation').get('send data').time)
        full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait, time_TR_1_wait, time_TR_2_wait,
                    time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                    label, log_option=index_run < 1)
        # full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait, time_TR_1_wait, time_TR_2_wait,
        #             time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
        #             label,function=np.min )
        # full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait, time_TR_1_wait, time_TR_2_wait,
        #             time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
        #             label,function=np.max )
    plt.show()
