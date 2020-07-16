import numpy as np
import matplotlib.pyplot as plt
from nest_elephant_tvb.simulation.file_translation.science_nest_to_tvb import slidding_window

def compute_rate(data,time,N,Dt):
    """
    Compute the firing rate
    :param data: the spike of all neurons between end and begin
    :return: the mean and the standard deviation of firing rate, the maximum and minimum of firing rate
    """
    #get data
    n_fil = np.searchsorted(time,data)
    n_fil = n_fil.astype(int)
    #count the number of the same id
    count_of_t = np.bincount(n_fil)
    #compute the rate
    rate_each_t_incomplet = count_of_t / float(N)
    rate_each_t = np.concatenate(
        (rate_each_t_incomplet, np.zeros(len(time)-np.shape(rate_each_t_incomplet)[0] )))
    return rate_each_t/(Dt*1e-3)

def bin_array(array, BIN, time_array,N,Dt):
    """
    compute rate and return the result and sliding windows
    :param array: spike trains
    :param BIN: width of the window
    :param time_array: time of histogram
    :param N: number of neurons
    :param Dt: integration time
    :return:
    """
    hist = compute_rate(array,time_array,N,Dt)
    return ( slidding_window(time_array,BIN),slidding_window(hist,BIN),hist)

def print_nest_pop(param, begin, end, spikes_ex, spikes_in, V_ex=None, V_in=None, W_ex=None, W_in=None, histogram=True):
    """
    print the result of the recording from Nest
    :param param: parameter of the simulation
    :param begin: start of recording
    :param end: end of recording
    :param spikes_ex: spike trains of the excitatory neurons
    :param spikes_in: spike trains of the inhibitory neurons
    :param V_ex: Voltage membrane of excitatory neurons
    :param V_in: Voltage membrane of inhibitory neurons
    :param W_ex: Adaptation of excitatory neurons
    :param W_in: Adaptation of inhibitory neurons
    :param histogram: bool for plotting or not the histogram
    :return:
    """
    dt = param['param_nest']["sim_resolution"]
    bin = int(param['param_tvb_model']['T'])
    nb_in = int(
        param['param_nest_topology']["nb_neuron_by_region"] * param['param_nest_topology']["percentage_inhibitory"])
    nb_ex = int(param['param_nest_topology']["nb_neuron_by_region"] - nb_in)

    total_time = end - begin
    time_array = np.arange(0, total_time + 1 + dt, dt)
    TimBinned_ex, popRate_ex, hist_ex = bin_array(np.concatenate(spikes_ex[1]) - begin, bin, time_array, nb_ex, dt)
    TimBinned_in, popRate_in, hist_in = bin_array(np.concatenate(spikes_in[1]) - begin, bin, time_array, nb_in, dt)

    if V_ex is not None:
        time_V_ex = V_ex[1]
        mean_V_ex = np.mean(V_ex[2], axis=0)
        max_V_ex = np.max(V_ex[2], axis=0)
        min_V_ex = np.min(V_ex[2], axis=0)
        time_W_ex = W_ex[1]
        mean_W_ex = np.mean(W_ex[2], axis=0)
        max_W_ex = np.max(W_ex[2], axis=0)
        min_W_ex = np.min(W_ex[2], axis=0)
        time_V_in = V_in[1]
        mean_V_in = np.mean(V_in[2], axis=0)
        max_V_in = np.max(V_in[2], axis=0)
        min_V_in = np.min(V_in[2], axis=0)
        time_W_in = W_in[1]
        mean_W_in = np.mean(W_in[2], axis=0)
        max_W_in = np.max(W_in[2], axis=0)
        min_W_in = np.min(W_in[2], axis=0)

        fig = plt.figure(figsize=(9.5, 8))
        ax1 = fig.add_subplot(221)
        ax2 = fig.add_subplot(222)

        for a in range(10):
            ax1.plot(V_ex[1], V_ex[2][a], 'b:', linewidth=0.5)
            ax1.plot(V_in[1], V_in[2][a], 'r:', linewidth=0.5)

        for a in range(10):
            ax2.plot(W_ex[1], W_ex[2][a], 'b:', linewidth=0.5)
            ax2.plot(W_in[1], W_in[2][a], 'r:', linewidth=0.5)

        ax1.plot(time_V_ex, mean_V_ex, 'b', linewidth=2.0)
        ax2.plot(time_W_ex, mean_W_ex, 'b', linewidth=2.0)
        ax1.plot(time_V_in, mean_V_in, 'r', linewidth=2.0)
        ax2.plot(time_W_in, mean_W_in, 'r', linewidth=2.0)
        # ax1.plot(time_V_ex, max_V_ex,'b--',linewidth=0.5)
        ax2.plot(time_W_ex, max_W_ex, 'b--', linewidth=1.0)
        # ax1.plot(time_V_in, max_V_in,'r--',linewidth=0.5)
        ax2.plot(time_W_in, max_W_in, 'r--', linewidth=1.0)
        # ax1.plot(time_V_ex, min_V_ex,'b--',linewidth=0.5)
        ax2.plot(time_W_ex, min_W_ex, 'b--', linewidth=1.0)
        # ax1.plot(time_V_in, min_V_in,'r--',linewidth=0.5)
        ax2.plot(time_W_in, min_W_in, 'r--', linewidth=1.0)

        ax1.set_ylim([-100, 0])
        ax1.set_xlabel('Time (ms)')
        ax1.set_ylabel('V in (mV)')
        ax2.set_xlabel('Time (ms)')
        ax2.set_ylabel('W in (pA)')

        ax3 = fig.add_subplot(223)
        for i in range(spikes_ex[0].shape[0]):
            ax3.plot(spikes_ex[1][i] - begin, np.repeat(spikes_ex[0][i], spikes_ex[1][i].shape[0]), '.b',
                     markersize=0.1)
        for i in range(spikes_in[0].shape[0]):
            ax3.plot(spikes_in[1][i] - begin, np.repeat(spikes_in[0][i], spikes_in[1][i].shape[0]), '.r',
                     markersize=0.1)
        ax3.set_xlabel('Time (ms)')
        ax3.set_ylabel('Neuron index')

        ax4 = fig.add_subplot(224)
        ax4.plot(TimBinned_ex, popRate_ex, 'b')
        ax4.plot(TimBinned_in, popRate_in, 'r')
        ax4.set_xlabel('Time (ms)')
        ax4.set_ylabel('FR')

        if histogram:
            plt.figure(figsize=(9.5, 4))
            plt.subplot(211)
            plt.plot(hist_ex, 'b')
            plt.title('Instantaneous firing rate of excitatory population')
            plt.xlabel('time in ms')
            plt.ylabel('Instantaneous firing rate in Hz')
            plt.subplot(212)
            plt.plot(hist_in, 'r')
            plt.title('Instantaneous firing rate of inhibitory population')
            plt.xlabel('time in ms')
            plt.ylabel('Instantaneous firing rate in Hz')
            plt.subplots_adjust(hspace=0.5)
    else:
        fig = plt.figure(figsize=(9.5, 4))
        ax3 = fig.add_subplot(121)
        for i in range(spikes_ex[0].shape[0]):
            ax3.plot(spikes_ex[1][i] - begin, np.repeat(spikes_ex[0][i], spikes_ex[1][i].shape[0]), '.b',
                     markersize=0.1)
        for i in range(spikes_in[0].shape[0]):
            ax3.plot(spikes_in[1][i] - begin, np.repeat(spikes_in[0][i], spikes_in[1][i].shape[0]), '.r',
                     markersize=0.1)
        ax3.set_xlabel('Time (ms)')
        ax3.set_ylabel('Neuron index')

        ax4 = fig.add_subplot(122)
        ax4.plot(TimBinned_ex, popRate_ex, 'b')
        ax4.plot(TimBinned_in, popRate_in, 'r')
        ax4.set_xlabel('Time (ms)')
        ax4.set_ylabel('FR')

        if histogram:
            plt.figure(figsize=(9.5, 4))
            plt.subplot(211)
            plt.plot(hist_ex, 'b')
            plt.title('Instantaneous firing rate of excitatory population')
            plt.xlabel('time in ms')
            plt.ylabel('Instantaneous firing rate in Hz')
            plt.subplot(212)
            plt.plot(hist_in, 'r')
            plt.title('Instantaneous firing rate of inhibitory population')
            plt.xlabel('time in ms')
            plt.ylabel('Instantaneous firing rate in Hz')
            plt.subplots_adjust(hspace=0.5)
    plt.show()

# Test the function, helping for debugging
if __name__ == '__main__':
    from nest_elephant_tvb.analyse.get_data import get_data_all
    data = get_data_all('/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/example/test_sim_2/nest/')
    param={}
    param['param_nest']={}
    param['param_nest']["sim_resolution"]=0.1
    param['param_tvb_model']={}
    param['param_tvb_model']['T']=20.0
    param['param_nest_topology']={}
    param['param_nest_topology']["percentage_inhibitory"] =0.2
    param['param_nest_topology']["nb_neuron_by_region"] =1000
    print_nest_pop(param, 0.0, 100.0,data['pop_1_ex'],data['pop_1_in'],
               V_ex=data['pop_1_ex_VM'],V_in=data['pop_1_in_VM'],
               W_ex=data['pop_1_ex_W'],W_in=data['pop_1_in_W'],
                histogram=True)