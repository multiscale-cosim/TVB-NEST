from timer.get_time_data import get_dictionnary
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    folders =[
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/100/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/1000/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000/_g_1.0_mean_I_ext_0.0/',
    ]
    time_sim = []
    time_nest_sim = []
    time_nest_IO =[]
    time_nest_tot =[]
    time_TVB_sim = []
    time_TVB_IO = []
    time_TVB_tot = []
    for i in folders:
        dict, index = get_dictionnary(i)
        time_sim.append(dict.get('Nest').time)
        time_nest_sim.append(dict.get('Nest').get('simulation').get('run').get('run simulation').time)
        diff = dict.get('TVB').get('simulation').get('run simulation').time - dict.get('Nest').get('simulation').get('run').get('run simulation').time
        if diff <0:
            diff =0
        time_nest_IO.append(dict.get('Nest').get('simulation').get('run').get('pre-run:<br>-waiting data<br>-update<br>stimulus<br>devices').time
                            +dict.get('Nest').get('simulation').get('run').get('post-run').time-diff)
        time_nest_tot.append(dict.get('Nest').get('simulation').get('run').get('run simulation').time+dict.get('Nest').get('simulation').get('run').get('pre-run:<br>-waiting data<br>-update<br>stimulus<br>devices').time
                    +dict.get('Nest').get('simulation').get('run').get('post-run').time-diff)
        time_TVB_sim.append(dict.get('TVB').get('simulation').get('run simulation').time)
        time_TVB_IO.append(dict.get('TVB').get('simulation').get('receive data').time - dict.get('TVB').get('simulation').get('receive data').get('wait receive').time
                        +dict.get('TVB').get('simulation').get('send data').time-dict.get('TVB').get('simulation').get('send data').get('wait send').time)
        time_TVB_tot.append(dict.get('TVB').get('simulation').get('run simulation').time
            +dict.get('TVB').get('simulation').get('receive data').time - dict.get('TVB').get('simulation').get('receive data').get('wait receive').time
                           +dict.get('TVB').get('simulation').get('send data').time-dict.get('TVB').get('simulation').get('send data').get('wait send').time)

    plt.figure(figsize=(20,20))
    plt.hlines(y=0.0,xmin=20,xmax=20000,color='k')
    plt.plot([20,200,2000,20000],time_sim)
    plt.plot([20,200,2000,20000],time_sim,'r',label='Simulation time')
    plt.plot([20,200,2000,20000],time_nest_IO,'--b', label='Nest : time of communication')
    plt.plot([20,200,2000,20000],time_nest_tot,'-b', label='Nest : time of I/O and simulation')
    plt.fill_between([20,200,2000,20000],time_nest_tot,time_nest_IO,color='b',alpha=0.2,label='Nest : time of simulation')
    plt.plot([20,200,2000,20000],time_TVB_IO,'--g', label='TVB  : time of communication')
    plt.plot([20,200,2000,20000],time_TVB_tot,'-g',label='TVB  : time of I/O and simulation')
    plt.fill_between([20,200,2000,20000],time_TVB_tot,time_TVB_IO,color='g',alpha=0.2,label='TVB : time of simulation')
    handles, labels = plt.gca().get_legend_handles_labels()
    order_element = [0,1,2,5,3,4,6]
    handles = [ handles[i] for i in order_element]
    labels = [labels[i] for i in order_element]
    plt.legend(handles,labels,fontsize=22)
    plt.xscale("log")
    plt.xlabel('number of neurons simulate with Nest',fontsize=30)
    plt.ylabel('wall time in s',fontsize=30)
    plt.title('Simulation time',fontsize=30)
    plt.tick_params(axis='both',labelsize=20)

    # folders =[
    #     '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000/_g_1.0_mean_I_ext_0.0/',
    #     '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000_2/_g_1.0_mean_I_ext_0.0/',
    #     '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000_3/_g_1.0_mean_I_ext_0.0/',
    #     '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000_4/_g_1.0_mean_I_ext_0.0/',
    # ]
    # time_sim = []
    # for i in folders:
    #     dict, index = get_dictionnary(i)
    #     time_sim.append(dict.get('Nest').time)
    #
    # plt.figure(figsize=(20,20))
    # plt.plot([1,2,3,4],time_sim)
    # plt.xlabel('number of MPI process',fontsize=30)
    # plt.ylabel('wall time in s',fontsize=30)
    # plt.title('Simulation time depending of the number of MPI process for Nest',fontsize=30)
    # plt.tick_params(axis='both',labelsize=20)
    # plt.show()

    folders =[
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/1/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/2/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/3/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/4/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/5/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/6/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/7/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/8/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/9/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/new_2/10000/10/_g_1.0_mean_I_ext_0.0/',
    ]
    time_sim = []
    time_nest_sim = []
    time_nest_IO =[]
    time_nest_tot =[]
    time_TVB_sim = []
    time_TVB_IO = []
    time_TVB_tot = []
    for i in folders:
        dict, index = get_dictionnary(i)
        time_sim.append(dict.get('Nest').time)
        time_nest_sim.append(dict.get('Nest').get('simulation').get('run').get('run simulation').time)
        diff = dict.get('TVB').get('simulation').get('run simulation').time - dict.get('Nest').get('simulation').get('run').get('run simulation').time
        if diff <0:
            diff =0
        time_nest_IO.append(dict.get('Nest').get('simulation').get('run').get('pre-run:<br>-waiting data<br>-update<br>stimulus<br>devices').time
                            +dict.get('Nest').get('simulation').get('run').get('post-run').time
                            -diff)
        time_nest_tot.append(dict.get('Nest').get('simulation').get('run').get('run simulation').time+dict.get('Nest').get('simulation').get('run').get('pre-run:<br>-waiting data<br>-update<br>stimulus<br>devices').time
                    +dict.get('Nest').get('simulation').get('run').get('post-run').time-diff)
        time_TVB_sim.append(dict.get('TVB').get('simulation').get('run simulation').time)
        time_TVB_IO.append(dict.get('TVB').get('simulation').get('receive data').time - dict.get('TVB').get('simulation').get('receive data').get('wait receive').time
                        +dict.get('TVB').get('simulation').get('send data').time-dict.get('TVB').get('simulation').get('send data').get('wait send').time)
        time_TVB_tot.append(dict.get('TVB').get('simulation').get('run simulation').time
            +dict.get('TVB').get('simulation').get('receive data').time - dict.get('TVB').get('simulation').get('receive data').get('wait receive').time
                           +dict.get('TVB').get('simulation').get('send data').time-dict.get('TVB').get('simulation').get('send data').get('wait send').time)



    plt.figure(figsize=(20,20))
    plt.hlines(y=0.0,xmin=1,xmax=10,color='k')
    plt.plot([1,2,3,4,5,6,7,8,9,10],time_sim,'r',label='Simulation time')
    plt.plot([1,2,3,4,5,6,7,8,9,10],time_nest_IO,'--b', label='Nest : time of communication')
    plt.plot([1,2,3,4,5,6,7,8,9,10],time_nest_tot,'-b', label='Nest : time of I/O and simulation')
    plt.fill_between([1,2,3,4,5,6,7,8,9,10],time_nest_tot,time_nest_IO,color='b',alpha=0.2,label='Nest : time of simulation')
    plt.plot([1,2,3,4,5,6,7,8,9,10],time_TVB_IO,'--g', label='TVB  : time of communication')
    plt.plot([1,2,3,4,5,6,7,8,9,10],time_TVB_tot,'-g',label='TVB  : time of I/O and simulation')
    plt.fill_between([1,2,3,4,5,6,7,8,9,10],time_TVB_tot,time_TVB_IO,color='g',alpha=0.2,label='TVB : time of simulation')
    plt.xlabel('number of MPI process',fontsize=30)
    plt.ylabel('wall time in s',fontsize=30)
    plt.title('Simulation time depending of the number of MPI process for Nest',fontsize=30)
    plt.tick_params(axis='both',labelsize=20)
    handles, labels = plt.gca().get_legend_handles_labels()
    order_element = [0,1,2,5,3,4,6]
    handles = [ handles[i] for i in order_element]
    labels = [labels[i] for i in order_element]
    plt.legend(handles, labels,fontsize=22)
    plt.show()

    folders =[
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/0.1/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/0.2/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/0.4/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/0.5/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/0.8/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/0.9/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/1.0/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/1.1/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/1.3/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/1.5/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/1.6/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/1.7/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/1.8/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/2.0/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/2.1/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/2.2/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/2.5/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/2.6/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/2.7/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/3.0/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/3.1/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/3.2/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/3.4/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/timer/test_file/time_syn/10000/3.5/_g_1.0_mean_I_ext_0.0/',
    ]
    time_sim = []
    time_nest_sim = []
    time_nest_IO =[]
    time_nest_tot =[]
    time_TVB_sim = []
    time_TVB_IO = []
    time_TVB_tot = []
    for i in folders:
        dict, index = get_dictionnary(i)
        time_sim.append(dict.get('Nest').time)
        time_nest_sim.append(dict.get('Nest').get('simulation').get('run').get('run simulation').time)
        diff = dict.get('TVB').get('simulation').get('run simulation').time - dict.get('Nest').get('simulation').get('run').get('run simulation').time
        if diff <0:
            diff =0
        time_nest_IO.append(dict.get('Nest').get('simulation').get('run').get('pre-run:<br>-waiting data<br>-update<br>stimulus<br>devices').time
                            +dict.get('Nest').get('simulation').get('run').get('post-run').time
                            -diff)
        time_nest_tot.append(dict.get('Nest').get('simulation').get('run').get('run simulation').time+dict.get('Nest').get('simulation').get('run').get('pre-run:<br>-waiting data<br>-update<br>stimulus<br>devices').time
                    +dict.get('Nest').get('simulation').get('run').get('post-run').time-diff)
        time_TVB_sim.append(dict.get('TVB').get('simulation').get('run simulation').time)
        time_TVB_IO.append(dict.get('TVB').get('simulation').get('receive data').time - dict.get('TVB').get('simulation').get('receive data').get('wait receive').time
                        +dict.get('TVB').get('simulation').get('send data').time-dict.get('TVB').get('simulation').get('send data').get('wait send').time)
        time_TVB_tot.append(dict.get('TVB').get('simulation').get('run simulation').time
            +dict.get('TVB').get('simulation').get('receive data').time - dict.get('TVB').get('simulation').get('receive data').get('wait receive').time
                           +dict.get('TVB').get('simulation').get('send data').time-dict.get('TVB').get('simulation').get('send data').get('wait send').time)



    plt.figure(figsize=(20,20))
    plt.hlines(y=0.0,xmin=0.1,xmax=3.6,color='k')
    x = [0.1,0.2,0.4,0.5,0.8,0.9,1.0,1.1,1.3,1.5,1.6,1.7,1.8,2.0,2.1,2.2,2.5,2.6,2.7,3.0,3.1,3.2,3.4,3.5]
    plt.plot(x,time_sim,'r',label='Simulation time')
    plt.plot(x,time_nest_IO,'--b', label='Nest : time of communication')
    plt.plot(x,time_nest_tot,'-b', label='Nest : time of I/O and simulation')
    plt.fill_between(x,time_nest_tot,time_nest_IO,color='b',alpha=0.2,label='Nest : time of simulation')
    plt.plot(x,time_TVB_IO,'--g', label='TVB  : time of communication')
    plt.plot(x,time_TVB_tot,'-g',label='TVB  : time of I/O and simulation')
    plt.fill_between(x,time_TVB_tot,time_TVB_IO,color='g',alpha=0.2,label='TVB : time of simulation')
    plt.xlabel('time of synchronization',fontsize=30)
    plt.ylabel('wall time in ms',fontsize=30)
    plt.title('Simulation time depending of the synchronization time',fontsize=30)
    plt.tick_params(axis='both',labelsize=20)
    handles, labels = plt.gca().get_legend_handles_labels()
    order_element = [0,1,2,5,3,4,6]
    handles = [ handles[i] for i in order_element]
    labels = [labels[i] for i in order_element]
    plt.legend(handles, labels,fontsize=22)

    plt.figure(figsize=(20,20))
    plt.plot(x,time_nest_IO/np.max(time_nest_IO)*100)
    plt.ylabel('percentage of the time of communication\nfor time of synchronization =0.1ms',fontsize=30)
    plt.xlabel('time of synchronization',fontsize=30)

    plt.show()