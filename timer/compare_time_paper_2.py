#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
import numpy as np
from timer.compare_time_paper import full_figure

# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    mpi = False
    folders_list = [
        # ('./test_file/paper_mpi/',np.arange(1,13,1),'only MPI'),
        ('./test_file/paper_time_thread/', np.arange(1, 13, 1), 'only Thread'),
        ('./test_file/paper_mpi_vp_2/', np.arange(2, 13, 2), 'Thread  and 2 MPI'),
        ('./test_file/paper_mpi_vp_4/', np.arange(4, 13, 4), 'Thread  and 4 MPI'),
    ]  # same data for the three case
    folders = [[] for i in folders_list]  # same data for the three case
    data = [[] for i in folders_list]     # same data for the three case
    nb_trial = 1  # the number of trial
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
                print(name_folder + '/' + str(trial) + '/_g_5.0_mean_I_ext_0.0/')
                tree, index = get_dictionnary(name_folder + '/' + str(trial) + '/_g_5.0_mean_I_ext_0.0/', mpi)
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
    figs = []
    titles = ['nest_sim', 'nest_IO', 'tvb_sim', 'sim']
    color = ['r', 'g', 'b', 'm']
    axes = []
    for i in range(len(titles)):
        figs.append(plt.figure())
        figs[i].add_subplot(1, 1, 1)
        axes.append(figs[i].get_axes()[0])
    for i in range(len(folders_list)):
        axes[0].plot(folders_list[i][1], data[i]['nest_sim'], color[i], marker='x', label=folders_list[i][2])
        axes[1].plot(folders_list[i][1], data[i]['nest_IO'], color[i], marker='x', label=folders_list[i][2])
        axes[2].plot(folders_list[i][1], data[i]['tvb_sim'], color[i], marker='x', label=folders_list[i][2])
        axes[3].plot(folders_list[i][1], data[i]['sim'], color[i], marker='x', label=folders_list[i][2])
    for i in range(len(axes)):
        axes[i].legend()
        axes[i].set_title(titles[i])
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(20, 20))
    fig.suptitle('Mean performance of 10 runs for 20000 neurons with Nest', fontsize=20)
    axes = [ax1, ax2, ax3, ax4]
    titles = ['time of the co-simulation', 'time of Nest IO', 'time of Nest simulation', 'time of TVB simulation']
    for i in range(len(folders_list)):
        axes[0].plot(folders_list[i][1], data[i]['sim'], color[i], marker='x', label=folders_list[i][2])
        axes[1].plot(folders_list[i][1], data[i]['nest_IO'], color[i], marker='x', label=folders_list[i][2])
        axes[2].plot(folders_list[i][1], data[i]['nest_sim'], color[i], marker='x', label=folders_list[i][2])
        axes[3].plot(folders_list[i][1], data[i]['tvb_sim'], color[i], marker='x', label=folders_list[i][2])
    for i in range(len(figs)):
        axes[i].legend(fontsize=15)
        axes[i].set_title(titles[i], fontdict={'fontsize': 18})
        axes[i].tick_params(axis='both', labelsize=15)
        axes[i].set_ylabel('Wall time of the simulation in s', fontsize=18)

    axes[-1].set_xlabel('number of virtual process', fontsize=18)
    plt.subplots_adjust(hspace=0.3)
    plt.show()
