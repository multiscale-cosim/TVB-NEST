#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.plot_result.get_time_data import get_dictionnary
from timer.plot_result.compare_time_paper import full_figure
import matplotlib.pyplot as plt
import numpy as np


# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    folders_list = [
        ('./test_file/jusuf/paper_neuron/',
         np.array(np.around(np.logspace(3,6,10))[:6]*2,dtype=int),
         'number of neurons simulated with Nest'),
         ('./test_file/jusuf/test_time/', [ 0.4, 0.5, 0.8, 0.9, 1.0, 1.1, 1.3, 1.5, 1.6, 1.7, 1.8, 2.0, 2.1],
          'time of synchronization between Nest and TVB (in ms)'),
        ('./test_file/jusuf/paper_mpi/', np.arange(1, 11, 1),
         'number of node use by Nest ( 1 MPI per node)'),
    ]  # same data for the three case
    mpi = True
    folders = [[] for i in folders_list]  # same data for the three case
    data = [[] for i in folders_list]  # same data for the three case
    nb_trial = 10  # the number of trial
    for index, (folder, list_nb, label) in enumerate(folders_list):
        for nb in list_nb:
            if index == 0:
                folders[index].append(folder + str(nb//2))
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
        full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                    time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                    label, log_option=index_run < 1)
        full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                    time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                    label,function=np.min )
        full_figure(list_nb, time_sim, time_nest_sim, time_nest_IO, time_nest_wait,
                    time_nest_tot, time_TVB_sim, time_TVB_IO, time_TVB_tot,
                    label,function=np.max )
    plt.show()
