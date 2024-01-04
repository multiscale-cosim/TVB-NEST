#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.plot_result.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.text import Text
from timer.plot_result.compare_time_paper import full_figure
from matplotlib import rcParams, font_manager
for s in font_manager.get_fontconfig_fonts():
    if s.find('Myria') != -1:
        font_manager.fontManager.addfont(s)
rcParams['font.family'] = 'Myriad Pro'

# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    import os

    path_global = os.path.dirname(os.path.realpath(__file__))
    mpi = False
    figsize = (10.0, 10.0)  # (20, 20)
    labelfont = 20
    labelfontlegend = 18
    ticks_size = 18

    folders_list = [
        (path_global + '/../../data/timer/paper_mpi/', np.arange(1, 13, 1), 'only MPI'),
        (path_global + '/../../data/timer/paper_time_thread/', np.arange(1, 13, 1), 'only Thread'),
        (path_global + '/../../data/timer/paper_mpi_vp_2/', np.arange(2, 13, 2), 'Thread  and 2 MPI'),
        (path_global + '/../../data/timer/paper_mpi_vp_4/', np.arange(4, 13, 4), 'Thread  and 4 MPI'),
    ]  # same data for the three case
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
        # full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait, time_TR_1_wait, time_TR_2_wait,
        #         time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
        #         label )
        # full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait, time_TR_1_wait, time_TR_2_wait,
        #             time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
        #             label,function=np.min )
        # full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait, time_TR_1_wait, time_TR_2_wait,
        #             time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
        #             label,function=np.max )
        data[index_run]['nest_sim'] = np.mean(time_nest_sim, axis=1)
        data[index_run]['nest_IO'] = np.mean(time_nest_IO, axis=1)
        data[index_run]['tvb_sim'] = np.mean(time_TVB_sim, axis=1)
        data[index_run]['sim'] = np.mean(time_sim, axis=1)

    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=figsize)
    # fig.suptitle('Mean performance of 10 runs for 20000 neurons with NEST', fontsize=20)
    data_name = ['sim', 'nest_IO', 'nest_sim', 'tvb_sim']
    axes = [ax1, ax2, ax3, ax4]
    color = ['r', 'c', 'b', 'm']
    markers = ['x', 'd', 'H', "^"]
    titles = ['Time of the co-simulation', 'Time of NEST IO', 'Time of NEST simulation', 'Time of TVB simulation']
    max = [0 for i in range(len(axes))]
    for axe_id in range(len(axes)):
        for i in range(len(data)):
            if max[axe_id] < data[i][data_name[axe_id]].max():
                max[axe_id] = data[i][data_name[axe_id]].max()
    plt.close('all')
    axe_id = 0
    plt.figure(figsize=figsize)
    for i in range(len(data)):
        plt.plot(folders_list[i][1], data[i][data_name[axe_id]], color[i], marker=markers[i], markersize=10, label=folders_list[i][2],
                 linewidth=2.0)
    plt.vlines(8, 0, max[axe_id], linestyles='dashed')
    plt.legend(fontsize=labelfontlegend)
    # plt.title(titles[axe_id], fontdict={'fontsize': labelfont})
    plt.tick_params(axis='both', labelsize=ticks_size)
    plt.ylabel('Wall clock time of the simulation in s', fontsize=labelfont)
    plt.xlabel('Number of virtual processes of NEST', fontsize=labelfont)
    plt.subplots_adjust(left=0.09, right=0.99, bottom=0.06, top=0.99)
    # plt.show()
    plt.savefig(path_global + '/../../data/figure/timer/compare_presentation.pdf', dpi=300)
    plt.savefig(path_global + '/../../data/figure/timer/compare_presentation.png', dpi=300)


