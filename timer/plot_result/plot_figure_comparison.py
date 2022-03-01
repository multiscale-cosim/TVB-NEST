#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.plot_result.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np


def print_time(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
               time_TVB_sim, time_TVB_IO,
               ax,
               function=np.mean,
               log_option=False,
               ylabel='Wall time of the simulation in s',
               xlabel='Wall time of the simulation in s',
               font_ticks_size=7,
               legend_position=1
               ):
    """
    create figure for comparison time of multiple configuration
    :param list_nb: list of increment of x axis
    :param time_sim: time of simulation
    :param time_nest_sim: time of nest simulation
    :param time_nest_IO: time of communication of nest
    :param time_nest_wait: time of waiting data by nest
    :param time_TVB_sim: time of simulation of TVB
    :param time_TVB_IO: time of communication of TVB
    :param ax: axis where to plot data
    :param function: function for grouping trial
    :param log_option: logarithm scale of x axis
    :param ylabel: label for axis y
    :param xlabel: label for axis x
    :param font_ticks_size: size of font ticks and label
    :param legend_position: position of the legend (see matplotlib)
    :return: figure
    """
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
    # plt.ylim(ymin=0.0)
    if log_option:
        plt.xscale('log')
    plt.legend(fontsize=font_ticks_size, loc=legend_position)
    plt.tick_params(axis='both', labelsize=font_ticks_size, pad=1)
    ax.set_ylabel(ylabel, fontsize=font_ticks_size, labelpad=0)
    ax.set_xlabel(xlabel, fontsize=font_ticks_size, labelpad=0)


def plot_compare(ax, data, folders_list,
                 ylabel='Wall time of the simulation in s',
                 xlabel='Number of virtual processes of NEST',
                 font_ticks_size=7,
                 legend_position=1, ymax=None):
    """

    :param data: data to plot
    :param folders_list: list of list of folders where are the data
    :param ylabel: label for axis y
    :param xlabel: label for axis x
    :param font_ticks_size: size of font ticks and label
    :param legend_position: position of the legend (see matplotlib)
    :param ymax: limit maximum of y
    :return:
    """
    color = ['r', 'c', 'b', 'm']
    markers = ['x', 'd', 'H', "^"]
    maximum = ymax
    for i in range(len(data)):
        if maximum < data[i]['sim'].max():
            maximum = data[i]['sim'].max()
    for i in range(len(data)):
        ax.plot(folders_list[i][1], data[i]['sim'], color[i], marker=markers[i],
                label=folders_list[i][2])
    ax.set_ylim(ymax=ymax)
    ax.vlines(8, 0, maximum, linestyles='dashed')
    plt.legend(fontsize=font_ticks_size, loc=legend_position)
    plt.tick_params(axis='both', labelsize=font_ticks_size)
    ax.set_ylabel(ylabel, fontsize=font_ticks_size, labelpad=2)
    ax.set_xlabel(xlabel, fontsize=font_ticks_size, labelpad=0)


def add_figure(ax, folder, list_nb, label, mpi=False, nb_trial=10, log_option=False, legend_position=1):
    """
    add a figure to plot
    :param ax: axis where to add figure
    :param folder: folder of hte data
    :param list_nb: list of trail
    :param label: label of the benchmark
    :param mpi: if the usage or not of MPI
    :param nb_trial: number of trial
    :param log_option: logarithmic scale
    :param legend_position: position of the legend (see matplotlib)
    :return:
    """
    folders = []
    for nb in list_nb:
        if log_option:  # not good but for the moment the only using log_scale
            folders.append(folder + str(nb // 2))
        else:
            folders.append(folder + str(nb))

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
    for index_folder, name_folder in enumerate(folders):
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
    print_time(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
               time_TVB_sim, time_TVB_IO, ax,
               xlabel=label, log_option=log_option, legend_position=legend_position)


def add_figure_compare(ax, folders_list, mpi=False, nb_trial=10, legend_position=1):
    """

    :param ax:
    :param folders_list:
    :param mpi:
    :param nb_trial:
    :param legend_position:
    :return:
    """
    data = [[] for i in folders_list]  # same data for the three case
    folders = [[] for i in folders_list]  # same data for the three case
    for index, (folder, list_nb, label) in enumerate(folders_list):
        for nb in list_nb:
            # the three test
            folders[index].append(folder + str(nb))
    for index_run, folder in enumerate(folders):
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
                tree, index = get_dictionnary(name_folder + '/' + str(trial) + '/_g_10.0_mean_I_ext_0.0/', mpi)
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
                    + tree.get('TVB').get('simulation').get('send data').time)
                time_TVB_tot[index_folder].append(
                    tree.get('TVB').get('simulation').get('run simulation').time
                    + tree.get('TVB').get('simulation').get('receive data').time
                    - tree.get('TVB').get('simulation').get('receive data').get('receive time').time
                    + tree.get('TVB').get('simulation').get('send data').time)
        data[index_run]['sim'] = np.mean(time_sim, axis=1)
    plot_compare(ax, data, folders_list, legend_position=legend_position, ymax=800)


# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    import os

    path_global = os.path.dirname(os.path.realpath(__file__))
    folders_list_one = [
        (path_global + '/../../data/timer/paper_nb_neurons/',
         np.array(np.around(np.logspace(1, 5, 30)) * 2, dtype=int),
         'Number of neurons simulated with NEST'),
        (path_global + '/../../data/timer/paper_time_synch/',
         [0.1, 0.2, 0.4, 0.5, 0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.6, 1.7, 1.8, 2.0, 2.1],
         'Time of synchronization between\n NEST and TVB (in ms)'),
    ]  # same data for the three case
    fig = plt.figure(figsize=(2.92, 5.35))
    grid = gridspec.GridSpec(3, 1, figure=fig)
    add_figure(fig.add_subplot(grid[0, 0]), folders_list_one[0][0], folders_list_one[0][1], folders_list_one[0][2],
               log_option=True, legend_position=2)
    add_figure(fig.add_subplot(grid[1, 0]), folders_list_one[1][0], folders_list_one[1][1], folders_list_one[1][2],
               log_option=False, legend_position=1)
    folders_list_compare = [
        (path_global + '/../../data/timer/paper_mpi/', np.arange(1, 13, 1), 'only MPI'),
        (path_global + '/../../data/timer/paper_time_thread/', np.arange(1, 13, 1), 'only Thread'),
        (path_global + '/../../data/timer/paper_mpi_vp_2/', np.arange(2, 13, 2), 'Thread  and 2 MPI'),
        (path_global + '/../../data/timer/paper_mpi_vp_4/', np.arange(4, 13, 4), 'Thread  and 4 MPI'),
    ]  # same data for the three case
    add_figure_compare(fig.add_subplot(grid[2, 0]), folders_list_compare, legend_position=2)

    plt.subplots_adjust(top=0.98, bottom=0.06, left=0.14, right=0.99, hspace=0.26, wspace=0.25)

    # plt.show()
    plt.savefig(path_global + '/../../data/figure/figure_3_compare.pdf')
