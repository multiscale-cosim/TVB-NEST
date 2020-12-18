#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
import numpy as np

# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    folders =[[],[],[]] # same data for the three case
    list_nb_neurons = np.around(np.logspace(1,4,30)) # list of the number of neurons
    nb_trial = 10 # the number of trial
    for nb_neurons in list_nb_neurons:
        # the three test
        folders[0].append('./test_file/benchmark_paper_ebrains/0.1/'+str(nb_neurons)+'/1/1/')
        folders[1].append('./test_file/benchmark_paper_ebrains/3.5/'+str(nb_neurons)+'/1/1/')
        folders[2].append('./test_file/benchmark_paper_ebrains/3.5/'+str(nb_neurons)+'/8/8/')
    # the label of the tree test
    labels = ['single-step synchronization between simulators','delayed synchronization between simulators','delayed synchronization between simulators \nand 8-threads-parallel NEST simulation']
    plt.figure(figsize=(20,20))
    for label,folder in zip(labels,folders):
        # get data
        time_sim = []
        time_nest_sim = []
        time_nest_IO =[]
        time_nest_wait = []
        time_TR_1_wait = []
        time_TR_2_wait = []
        time_nest_tot =[]
        time_TVB_sim = []
        time_TVB_IO = []
        time_TVB_tot = []
        for index_folder,name_folder in enumerate(folder):
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
                print(name_folder+'/'+str(trial)+'/_g_1.0_mean_I_ext_0.0/')
                dict, index = get_dictionnary(name_folder+'/'+str(trial)+'/_g_1.0_mean_I_ext_0.0/')
                time_sim[index_folder].append(dict.get('Nest').time)
                time_nest_sim[index_folder].append(dict.get('Nest').get('simulation').get('run').get('run simulation').time)
                time_nest_IO[index_folder].append(dict.get('Nest').get('simulation').get('run').get('pre-run').time
                                    -dict.get('Nest').get('simulation').get('run').get('pre-run').get('pre_run_input').get('pre_run_input_wait').time
                                    +dict.get('Nest').get('simulation').get('run').get('post-run').time)
                time_nest_wait[index_folder].append(dict.get('Nest').get('simulation').get('run').get('pre-run').get('pre_run_input').get('pre_run_input_wait').time)
                time_TR_1_wait[index_folder].append(dict.get('Translation TVB to Nest 0').get('simulation').get('send thread').get('wait for receiving thread').time)
                time_TR_2_wait[index_folder].append(dict.get('Translation TVB to Nest 1').get('simulation').get('send thread').get('wait for receiving thread').time)
                time_nest_tot[index_folder].append(dict.get('Nest').get('simulation').get('run').get('run simulation').time+dict.get('Nest').get('simulation').get('run').get('pre-run').get('pre_run_input').time
                                     +dict.get('Nest').get('simulation').get('run').get('post-run').time)
                time_TVB_sim[index_folder].append(dict.get('TVB').get('simulation').get('run simulation').time)
                time_TVB_IO[index_folder].append(dict.get('TVB').get('simulation').get('receive data').time - dict.get('TVB').get('simulation').get('receive data').get('wait receive').time
                                   +dict.get('TVB').get('simulation').get('send data').time-dict.get('TVB').get('simulation').get('send data').get('wait send').time)
                time_TVB_tot[index_folder].append(dict.get('TVB').get('simulation').get('run simulation').time
                                    +dict.get('TVB').get('simulation').get('receive data').time - dict.get('TVB').get('simulation').get('receive data').get('wait receive').time
                                    +dict.get('TVB').get('simulation').get('send data').time-dict.get('TVB').get('simulation').get('send data').get('wait send').time)

        # plot the result
        print("plot")
        plt.plot(list_nb_neurons*2,np.mean(time_sim,axis=1),'g-',label ='time sim' )
        plt.plot(list_nb_neurons*2,np.mean(time_TVB_tot,axis=1),'m-',label ='TVB total' )
        plt.plot(list_nb_neurons*2,np.mean(time_nest_sim,axis=1),'b-',label =' sim nest' )
        plt.plot(list_nb_neurons*2,np.mean(time_nest_IO,axis=1),'b--',label =' IO nest' )
        plt.plot(list_nb_neurons*2,np.mean(time_nest_wait,axis=1),'g--',label =' wait nest' )
        plt.plot(list_nb_neurons*2,np.mean(time_TR_1_wait,axis=1),color='tab:orange',label =' wait TR 1' )
        plt.plot(list_nb_neurons*2,np.mean(time_TR_2_wait,axis=1),'y',label =' wait TR 2' )
        plt.plot(list_nb_neurons*2,np.mean(time_TR_2_wait,axis=1)+np.mean(time_TR_1_wait,axis=1),'y',label =' sum' )
        plt.plot(list_nb_neurons*2,np.mean(time_nest_wait,axis=1)+np.mean(time_nest_IO,axis=1)+np.mean(time_nest_sim,axis=1),'m.-',label =' sum nest' )
        plt.plot(list_nb_neurons*2,np.mean(time_nest_IO,axis=1)+np.mean(time_nest_sim,axis=1),'b.-',label =' sum nest' )
        plt.plot(list_nb_neurons*2,np.mean(time_TVB_sim,axis=1),'r-',label = ' sim TVB ')
        plt.plot(list_nb_neurons*2,np.mean(time_TVB_IO,axis=1),'r--',label = ' IO TVB ' )
        plt.xscale('log')
        plt.legend(fontsize=20)
        print(label)
    # add labels and some configuration
    plt.ylabel('Wall time of the simulation in s',fontsize=30)
    plt.xlabel('Number of neurons in the spiking neural network',fontsize=30)
    plt.tick_params(axis='both',labelsize=20)
    plt.show()
