#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from timer.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
import numpy as np

# figure for the optimisation for the paper TVB-ebrains
if __name__ == '__main__':
    folders =[[]] # same data for the three case
    list_nb_neurons = np.array(np.around(np.logspace(1,4,30)),dtype=np.int) # list of the number of neurons
    nb_trial = 10 # the number of trial
    for nb_neurons in list_nb_neurons:
        # the three test
        folders[0].append('./test_file/benchmark_paper_ebrains/3.5/'+str(nb_neurons)+'/8/8/')
    # the label of the tree test
    labels = [
              'delayed synchronization between simulators \nand 8-threads-parallel NEST simulation'
              ]
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
        fig = plt.figure(figsize=(20, 20))

        # print time
        plt.subplot(121)
        ax = plt.gca()
        ax.fill_between(list_nb_neurons*2,
                        (np.mean(time_TVB_sim,axis=1)+np.mean(time_TVB_IO,axis=1)),
                        np.mean(time_sim,axis=1),
                        color='y',label ='simulation',alpha=0.2)
        ax.fill_between(list_nb_neurons*2,
                        np.zeros_like(np.mean(time_nest_sim,axis=1)),
                        (np.mean(time_nest_sim,axis=1)),
                        color=[255 / 255, 104 / 255, 65 / 255],label='sim nest', alpha=0.5, hatch='/')
        ax.fill_between(list_nb_neurons*2,
                        (np.mean(time_nest_sim,axis=1)),
                        (np.mean(time_nest_IO,axis=1)+np.mean(time_nest_sim,axis=1)),
                        color=[255 / 255, 104 / 255, 65 / 255],label ='IO nest',alpha=0.5,hatch='\\')
        ax.fill_between(list_nb_neurons*2,
                        (np.mean(time_nest_IO,axis=1)+np.mean(time_nest_sim,axis=1)),
                        (np.mean(time_nest_wait,axis=1)+np.mean(time_nest_IO,axis=1)+np.mean(time_nest_sim,axis=1)),
                        color=[255 / 255, 104 / 255, 65 / 255],label='wait nest',alpha=0.5,hatch='.')
        ax.fill_between(list_nb_neurons*2,
                        np.zeros_like(np.mean(time_TVB_sim,axis=1)),
                        (np.mean(time_TVB_sim,axis=1)),
                        color=[71 / 255, 164 / 255, 226 / 255],label='sim TVB',alpha=0.5)
        ax.fill_between(list_nb_neurons*2,
                        (np.mean(time_TVB_sim,axis=1)),
                        (np.mean(time_TVB_sim,axis=1)+np.mean(time_TVB_IO,axis=1)),
                        color=[71 / 255, 164 / 255, 226 / 255],label='IO TVB',alpha=0.5,hatch='\\')
        plt.ylim(ymin=0.0)
        plt.xscale('log')
        plt.legend(fontsize=20,loc=2)
        plt.tick_params(axis='both', labelsize=20)
        ax.set_ylabel('Wall time of the simulation in s', fontsize=20)

        # print percentage cumulative
        plt.subplot(222)
        print("plot")
        plt.plot(list_nb_neurons*2,(np.mean(time_nest_sim,axis=1)+np.mean(time_nest_IO,axis=1))/np.mean(time_sim,axis=1)*100,'-',
                 color=[255 / 255, 104 / 255, 65 / 255],label='sim nest')
        plt.plot(list_nb_neurons*2,(np.mean(time_nest_IO,axis=1))/np.mean(time_sim,axis=1)*100,'--',
                 color=[255 / 255, 104 / 255, 65 / 255],label='IO nest')
        plt.plot(list_nb_neurons*2,(np.mean(time_nest_wait,axis=1)+np.mean(time_nest_IO,axis=1)+np.mean(time_nest_sim,axis=1))/np.mean(time_sim,axis=1)*100,'-.',
                 color=[255 / 255, 104 / 255, 65 / 255],label='wait nest')
        plt.plot(list_nb_neurons*2,(np.mean(time_TVB_IO,axis=1)+np.mean(time_TVB_sim,axis=1))/np.mean(time_sim,axis=1)*100,'-',
                 color=[71 / 255, 164 / 255, 226 / 255],label='sim TVB')
        plt.plot(list_nb_neurons*2,(np.mean(time_TVB_IO,axis=1))/np.mean(time_sim,axis=1)*100,'--',
                 color=[71 / 255, 164 / 255, 226 / 255],label='IO TVB')
        plt.plot(list_nb_neurons*2,np.mean(time_sim,axis=1)/np.mean(time_sim,axis=1)*100,
                 'y-',label ='simulation')
        plt.ylim(ymin=0.0)
        plt.xscale('log')
        plt.tick_params(axis='both', labelsize=20)
        plt.legend(fontsize=20)
        plt.ylabel('cumulative percentage of\nsimulated time', fontsize=20,labelpad=-12)

        # print percentage
        plt.subplot(224)
        plt.plot(list_nb_neurons*2,(np.mean(time_nest_IO,axis=1))/np.mean(time_sim,axis=1)*100,'--',
                 color=[255 / 255, 104 / 255, 65 / 255],label ='IO nest')
        plt.plot(list_nb_neurons*2,(np.mean(time_nest_wait,axis=1))/np.mean(time_sim,axis=1)*100,'-.',
                 color=[255 / 255, 104 / 255, 65 / 255],label ='wait nest')
        plt.plot(list_nb_neurons*2,(np.mean(time_nest_sim,axis=1))/np.mean(time_sim,axis=1)*100,'-',
                 color=[255 / 255, 104 / 255, 65 / 255],label ='sim nest')
        plt.plot(list_nb_neurons*2,np.mean(time_sim,axis=1)/np.mean(time_sim,axis=1)*100,
                 'y-',label ='simulation' )
        plt.xscale('log')
        plt.ylim(ymin=0.0)
        plt.legend(fontsize=20)
        plt.tick_params(axis='both',labelsize=20)
        plt.ylabel('percentage of\nsimulated time', fontsize=20,labelpad=-12)

        # add labels and some configuration
        fig.text(0.5, 0.04, 'Number of neurons in the spiking neural network', ha='center', va='center', fontsize=20)

    plt.show()
