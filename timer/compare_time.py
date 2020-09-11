from timer.get_time_data import get_dictionnary
import matplotlib.pyplot as plt

if __name__ == '__main__':
    folders =[
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/100/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/1000/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000/_g_1.0_mean_I_ext_0.0/',
    ]
    time_sim = []
    for i in folders:
        dict, index = get_dictionnary(i)
        time_sim.append(dict.get('Nest').time)

    plt.figure(figsize=(20,20))
    plt.plot([20,200,2000,20000],time_sim)
    plt.xscale("log")
    plt.xlabel('number of neurons simulate with Nest',fontsize=30)
    plt.ylabel('wall time in s',fontsize=30)
    plt.title('Simulation time',fontsize=30)
    plt.tick_params(axis='both',labelsize=20)

    folders =[
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000_2/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000_3/_g_1.0_mean_I_ext_0.0/',
        '/home/kusch/Documents/project/co_simulation/TVB-NEST/tests/test_file/new/10000_4/_g_1.0_mean_I_ext_0.0/',
    ]
    time_sim = []
    for i in folders:
        dict, index = get_dictionnary(i)
        time_sim.append(dict.get('Nest').time)

    plt.figure(figsize=(20,20))
    plt.plot([1,2,3,4],time_sim)
    plt.xlabel('number of MPI process',fontsize=30)
    plt.ylabel('wall time in s',fontsize=30)
    plt.title('Simulation time depending of the number of MPI process for Nest',fontsize=30)
    plt.tick_params(axis='both',labelsize=20)
    plt.show()
