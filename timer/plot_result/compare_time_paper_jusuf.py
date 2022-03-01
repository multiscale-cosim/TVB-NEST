#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.plot_result.get_time_data import get_dictionnary
from timer.plot_result.compare_time_paper import full_figure
import matplotlib.pyplot as plt
from matplotlib.text import Text
import numpy as np
import os

# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    import os

    path_global = os.path.dirname(os.path.realpath(__file__))
    folders_list = [
        (path_global + '/../../data/timer/jusuf/paper_neuron/',
         np.array(np.around(np.logspace(3, 6, 10))[:6] * 2, dtype=int),
         'number of neurons simulated with NEST'),
        (path_global + '/../../data/timer/jusuf/test_time/', [0.4, 0.5, 0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.6, 1.7, 1.8, 2.0, 2.1],
         'time of synchronization between NEST and TVB (in ms)'),
        (path_global + '/../../data/timer/jusuf/paper_mpi/', np.arange(1, 11, 1),
         'number of node use by NEST ( 1 MPI per node)'),
    ]  # same data for the three case
    mpi = True
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
        time_nest_tot = []
        time_TVB_sim = []
        time_TVB_IO = []
        time_TVB_tot = []
        if not os.path.exists(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2]):
            os.mkdir(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2])
        for index_folder, name_folder in enumerate(folder):
            time_sim.append([])
            time_nest_sim.append([])
            time_nest_IO.append([])
            time_nest_wait.append([])
            time_nest_tot.append([])
            time_TVB_sim.append([])
            time_TVB_IO.append([])
            time_TVB_tot.append([])
            for trial in range(nb_trial):
                if index_run == 2:
                    print(name_folder + '/' + str(trial) + '/_g_5.0_mean_I_ext_0.0/')
                    tree = get_dictionnary(name_folder + '/' + str(trial) + '/_g_5.0_mean_I_ext_0.0/',
                                           mpi=mpi, transformation=False)
                else:
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
        wspase = 0.17 if index_run == 0 else 0.20
        fig = full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                    time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                    label, log_option=index_run < 1, wspase=wspase,
                    labelsize=7, labellegend=7, fontsize=7, figsize=(7.09, 7.28))
        fig.add_artist(Text(0.01, 0.98, "a", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.98, "b", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.49, "c", fontproperties={'size': 7}))
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_max.pdf', dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_mean.pdf', dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_mean.png', dpi=150)
        plt.close('all')
        fig = full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                    time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                    label, function=np.min, wspase=wspase,
                    labelsize=7, labellegend=7, fontsize=7, figsize=(7.09, 7.28))
        fig.add_artist(Text(0.01, 0.98, "a", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.98, "b", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.49, "c", fontproperties={'size': 7}))
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_max.pdf', dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_min.pdf', dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_min.png', dpi=150)
        plt.close('all')
        fig = full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                    time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                    label, function=np.max, wspase=wspase,
                    labelsize=7, labellegend=7, fontsize=7, figsize=(7.09, 7.28))
        fig.add_artist(Text(0.01, 0.98, "a", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.98, "b", fontproperties={'size': 7}))
        fig.add_artist(Text(0.5, 0.49, "c", fontproperties={'size': 7}))
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_max.pdf', dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_max.pdf', dpi=300)
        plt.savefig(path_global + '/../../data/figure/timer/jusuf_' + folder[0].split('/')[-2] + '/full_figure_max.png', dpi=150)
        plt.close('all')
    # plt.show()
