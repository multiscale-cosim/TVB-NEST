#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.plot_result.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
from matplotlib.text import Text
import numpy as np


def print_time(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
               time_TVB_sim, time_TVB_IO,
               title,
               function=np.mean,
               log_option=False,
               ylabel='Wall time of the simulation in s',
               labelsize=40,
               labellegend=30,
               figsize=(20, 20),
               wspase=0.17
               ):
    """
    create figure for comparison time of multiple configuration
    :param list_nb: list of increment of x axis
    :param time_sim: time of simulation
    :param time_nest_sim: time of nest simulation
    :param time_nest_IO: time of communication of nest
    :param time_nest_wait: time of waiting data by nest
    :param time_TR_1_wait: time of transformation wait
    :param time_TR_2_wait: time of transformation wait
    :param time_nest_tot: total time of NEST simulation
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
    fig = plt.figure(figsize=figsize)

    ax = plt.gca()
    ax.fill_between(list_nb,
                    (function(time_TVB_sim, axis=1) + function(time_TVB_IO, axis=1)),
                    function(time_sim, axis=1),
                    color='y', label='co-simulation', alpha=0.2)
    ax.fill_between(list_nb,
                    np.zeros_like(function(time_nest_sim, axis=1)),
                    (function(time_nest_sim, axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='NEST simulation', alpha=0.5, hatch='o')
    ax.fill_between(list_nb,
                    (function(time_nest_sim, axis=1)),
                    (function(time_nest_IO, axis=1) + function(time_nest_sim, axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='NEST IO', alpha=0.5, hatch='oo')
    ax.fill_between(list_nb,
                    (function(time_nest_IO, axis=1) + function(time_nest_sim, axis=1)),
                    (function(time_nest_wait, axis=1) + function(time_nest_IO, axis=1) + function(time_nest_sim,
                                                                                                  axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='NEST wait', alpha=0.5, hatch='.')
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
    plt.legend(fontsize=labellegend, loc=1)
    plt.tick_params(axis='both', labelsize=labelsize, pad=1)
    ax.set_ylabel(ylabel, fontsize=labelsize, labelpad=0)
    ax.set_xlabel('', fontsize=labelsize, labelpad=0)
    # add labels and some configuration
    fig.text(0.5, 0.04, title, ha='center', va='center', fontsize=labelsize)
    plt.subplots_adjust(left=0.13, right=0.99, top=0.97, bottom=0.13, wspace=wspase)
    return fig


def full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                title,
                function=np.mean,
                log_option=False,
                ylabel_1='Wall time of the simulation in s',
                ylabel_2='Stack of percentage of\nsimulated time',
                ylabel_3='Percentage of\nsimulated time',
                figsize=(20, 20),
                labelsize=20,
                labellegend=15,
                fontsize=20,
                wspase=0.17
                ):
    """
    create figure for comparison time of multiple configuration
    :param list_nb: list of increment of x axis
    :param time_sim: time of simulation
    :param time_nest_sim: time of nest simulation
    :param time_nest_IO: time of communication of nest
    :param time_nest_wait: time of waiting data by nest
    :param time_TR_1_wait: time of transformation wait
    :param time_TR_2_wait: time of transformation wait
    :param time_nest_tot: total time of NEST simulation
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
    fig = plt.figure(figsize=figsize)

    # print time
    plt.subplot(121)
    ax = plt.gca()
    ax.fill_between(list_nb,
                    (function(time_TVB_sim, axis=1) + function(time_TVB_IO, axis=1)),
                    function(time_sim, axis=1),
                    color='y', label='Co-simulation', alpha=0.2)
    ax.fill_between(list_nb,
                    np.zeros_like(function(time_nest_sim, axis=1)),
                    (function(time_nest_sim, axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='NEST simulation', alpha=0.5, hatch='o')
    ax.fill_between(list_nb,
                    (function(time_nest_sim, axis=1)),
                    (function(time_nest_IO, axis=1) + function(time_nest_sim, axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='NEST IO', alpha=0.5, hatch='oo')
    ax.fill_between(list_nb,
                    (function(time_nest_IO, axis=1) + function(time_nest_sim, axis=1)),
                    (function(time_nest_wait, axis=1) + function(time_nest_IO, axis=1) + function(time_nest_sim,
                                                                                                  axis=1)),
                    color=[255 / 255, 104 / 255, 65 / 255], label='NEST wait', alpha=0.5, hatch='.')
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
    plt.legend(fontsize=labellegend, loc=2)
    plt.tick_params(axis='both', labelsize=labelsize)
    ax.set_ylabel(ylabel_1, fontsize=fontsize)

    # print percentage cumulative
    plt.subplot(222)
    print("plot")
    plt.plot(list_nb,
             (function(time_nest_sim, axis=1) + function(time_nest_IO, axis=1)) / function(time_sim, axis=1) * 100, '-',
             color=[255 / 255, 104 / 255, 65 / 255], label='NEST simulation')
    plt.plot(list_nb, (function(time_nest_IO, axis=1)) / function(time_sim, axis=1) * 100, '--',
             color=[255 / 255, 104 / 255, 65 / 255], label='NEST IO')
    plt.plot(list_nb, (function(time_nest_wait, axis=1) + function(time_nest_IO, axis=1) + function(time_nest_sim,
                                                                                                    axis=1)) / function(
        time_sim, axis=1) * 100, '-.',
             color=[255 / 255, 104 / 255, 65 / 255], label='NEST wait')
    plt.plot(list_nb,
             (function(time_TVB_IO, axis=1) + function(time_TVB_sim, axis=1)) / function(time_sim, axis=1) * 100,
             '-',
             color=[71 / 255, 164 / 255, 226 / 255], label='TVB simulation')
    plt.plot(list_nb, (function(time_TVB_IO, axis=1)) / function(time_sim, axis=1) * 100, '--',
             color=[71 / 255, 164 / 255, 226 / 255], label='TVB IO')
    plt.plot(list_nb, function(time_sim, axis=1) / function(time_sim, axis=1) * 100,
             'y-', label='Co-simulation')
    plt.ylim(ymin=0.0)
    if log_option:
        plt.xscale('log')
    plt.tick_params(axis='both', labelsize=labelsize)
    plt.legend(fontsize=labellegend)
    plt.ylabel(ylabel_2, fontsize=fontsize, labelpad=-1)

    # print percentage
    plt.subplot(224)
    plt.plot(list_nb, (function(time_nest_IO, axis=1)), '--',
             color=[255 / 255, 104 / 255, 65 / 255], label='NEST IO')
    plt.plot(list_nb, (function(time_nest_wait, axis=1)), '-.',
             color=[255 / 255, 104 / 255, 65 / 255], label='NEST wait')
    plt.plot(list_nb, (function(time_nest_sim, axis=1)), '-',
             color=[255 / 255, 104 / 255, 65 / 255], label='NEST simulation')
    plt.ylim(ymin=0.0)
    if log_option:
        plt.xscale('log')
    plt.legend(fontsize=labellegend)
    plt.tick_params(axis='both', labelsize=labelsize)
    plt.ylabel(ylabel_3, fontsize=fontsize, labelpad=-1)

    # add labels and some configuration
    fig.text(0.5, 0.01, title, ha='center', va='center', fontsize=fontsize)
    plt.subplots_adjust(left=0.07, right=0.99, top=0.99, wspace=wspase, hspace=0.1, bottom=0.05)
    return fig


# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    import os

    path_global = os.path.dirname(os.path.realpath(__file__))
    folders_list = [
        (path_global + '/../../data/timer/paper_nb_neurons/',
         np.array(np.around(np.logspace(1, 5, 30)) * 2, dtype=int),
         'Number of neurons simulated with NEST'),
        (path_global + '/../../data/timer/paper_mpi/', np.arange(1, 13, 1),
         'Number of MPI using by NEST ( 1 MPI = 1 VP)'),
        (path_global + '/../../data/timer/paper_time_thread/', np.arange(1, 13, 1),
         'Number of virtual processes of NEST (number of MPI : 1)'),
        (path_global + '/../../data/timer/paper_mpi_vp_2/', np.arange(2, 13, 2),
         'Number of virtual processes of NEST (number of MPI : 2)'),
        (path_global + '/../../data/timer/paper_mpi_vp_4/', np.arange(4, 13, 4),
         'Number of virtual processes of NEST (number of MPI : 4)'),
        (path_global + '/../../data/timer/paper_time_synch/',
         [0.1, 0.2, 0.4, 0.5, 0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.6, 1.7, 1.8, 2.0, 2.1],
         'Time of synchronization between NEST and TVB (in ms)'),
    ]  # same data for the three case
    mpi = False
    folders = [[] for i in folders_list]  # same data for the three case
    data = [[] for i in folders_list]  # same data for the three case
    nb_trial = 10  # the number of trial
    for index, (folder, list_nb, label) in enumerate(folders_list):
        for nb in list_nb:
            if index == 0:
                folders[index].append(folder + str(nb // 2))
            else:
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
        if not os.path.exists(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2]):
            os.mkdir(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2])
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
                time_sim[index_folder].append(tree.get('NEST').time)
                time_nest_sim[index_folder].append(
                    tree.get('NEST').get('simulation nest').get('run').get('simulation kernel nest').time)
                time_nest_IO[index_folder].append(
                    tree.get('NEST').get('simulation nest').get('run').get('pre-run').time
                    - tree.get('NEST').get('simulation nest').get('run').get('pre-run').get(
                        'pre_run_input').get('pre_run_input_wait').time
                    + tree.get('NEST').get('simulation nest').get('run').get('post-run').time)
                time_nest_wait[index_folder].append(
                    tree.get('NEST').get('simulation nest').get('run').get('pre-run').get(
                        'pre_run_input').get('pre_run_input_wait').time)
                time_TR_1_wait[index_folder].append(
                    tree.get('TVB_NEST_0: Producer NEST data ').get('simulation').get('get internal spikes').get(
                        'wait read buffer').time)
                time_TR_2_wait[index_folder].append(
                    tree.get('TVB_NEST_1: Producer NEST data ').get('simulation').get('get internal spikes').get(
                        'wait read buffer').time)
                time_nest_tot[index_folder].append(
                    tree.get('NEST').get('simulation nest').get('run').get('simulation kernel nest').time
                    + tree.get('NEST').get('simulation nest').get('run').get('pre-run').get('pre_run_input').time
                    + tree.get('NEST').get('simulation nest').get('run').get('post-run').time)
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
        wspase = 0.17 if index_run != 5 else 0.20
        fig = full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                          time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                          label, log_option=index_run < 1, wspase=wspase,
                          labelsize=7, labellegend=7, fontsize=7, figsize=(7.09, 7.28))
        fig.add_artist(Text(0.01, 0.98, "a", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.98, "b", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.49, "c", fontproperties={'size': 7}))
        plt.savefig(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2] + '/full_figure_mean.pdf',
                    dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2] + '/full_figure_mean.png',
                    dpi=150)
        print_time(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                   time_TVB_sim, time_TVB_IO,
                   label, log_option=index_run < 1, wspase=wspase,
                   labelsize=7, labellegend=7, figsize=(7.09, 7.28))
        plt.savefig(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2] + '/full_figure_time.pdf',
                    dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2] + '/full_figure_time.png',
                    dpi=150)
        fig = full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                          time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                          label, function=np.min, log_option=index_run < 1, wspase=wspase,
                          labelsize=7, labellegend=7, fontsize=7, figsize=(7.09, 7.28))
        fig.add_artist(Text(0.01, 0.98, "a", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.98, "b", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.49, "c", fontproperties={'size': 7}))
        plt.savefig(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2] + '/full_figure_min.pdf',
                    dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2] + '/full_figure_min.png',
                    dpi=150)
        fig = full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                          time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                          label, function=np.max, log_option=index_run < 1, wspase=wspase,
                          labelsize=7, labellegend=7, fontsize=7, figsize=(7.09, 7.28))
        fig.add_artist(Text(0.01, 0.98, "a", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.98, "b", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.49, "c", fontproperties={'size': 7}))
        plt.savefig(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2] + '/full_figure_max.pdf',
                    dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/' + folder[0].split('/')[-2] + '/full_figure_max.png',
                    dpi=150)
        plt.close('all')
    # plt.show()
