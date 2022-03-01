#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
import matplotlib.pylab as plt

from analyse.LFPY.example_plotting import plot_signal_sum
from analyse.trial_print_figure_micro import bin_array


def print_nest_pop(param, begin, end, spikes_ex, spikes_in, V_ex=None, V_in=None, W_ex=None, W_in=None, path_LFP='.',
                   LFP_inc=200, size_neurons=0.1, xmin=None, xmax=None):
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
    :param path_LFP : path of LFP
    :param LFP_inc : space between LFP curve
    :param size_neurons : size of the marker for one spikes
    :param xmin : minimal limit of x
    :param xmax : maximal limit of x
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

    import matplotlib.ticker as tkr
    def numfmt(x, pos):  # your custom formatter function: divide by 100.0
        s = '{}'.format(x * dt)
        return s

    format_hixt_x = tkr.FuncFormatter(numfmt)

    if xmin is None:
        xmin = begin - 1.0
    if xmax is None:
        xmax = end + 1.0
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
        ax1 = fig.add_subplot(331)
        ax2 = fig.add_subplot(332)

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
        ax1.set_xlim([xmin, xmax])
        ax2.set_xlabel('Time (ms)')
        ax2.set_ylabel('W in (pA)')
        ax2.set_xlim([xmin, xmax])

        ax3 = fig.add_subplot(334)
        for i in range(spikes_ex[0].shape[0]):
            ax3.plot(spikes_ex[1][i] - begin, np.repeat(spikes_ex[0][i], spikes_ex[1][i].shape[0]), '.b',
                     markersize=size_neurons)
        for i in range(spikes_in[0].shape[0]):
            ax3.plot(spikes_in[1][i] - begin, np.repeat(spikes_in[0][i], spikes_in[1][i].shape[0]), '.r',
                     markersize=size_neurons)
        ax3.set_xlabel('Time (ms)')
        ax3.set_ylabel('Neuron index')
        ax3.set_xlim([xmin, xmax])

        ax4 = fig.add_subplot(335)
        ax4.plot(TimBinned_ex, popRate_ex, 'b', label='excitatory population')
        ax4.plot(TimBinned_in, popRate_in, 'r', label='inhibitory population')
        ax4.set_xlabel('Time (ms)')
        ax4.set_ylabel('FR')
        ax4.legend()
        ax4.set_xlim([xmin, xmax])

        plt.subplot(615)
        plt.plot(hist_ex, 'b')
        plt.title('Instantaneous firing rate of excitatory population')
        plt.xlabel('time in ms')
        plt.ylabel('Instantaneous firing rate\n in Hz')
        plt.gca().xaxis.set_major_formatter(format_hixt_x)
        plt.xlim([xmin * 10, xmax * 10])
        plt.subplot(616)
        plt.plot(hist_in, 'r')
        plt.title('Instantaneous firing rate of inhibitory population')
        plt.xlabel('time in ms')
        plt.ylabel('Instantaneous firing rate \nin Hz')
        plt.gca().xaxis.set_major_formatter(format_hixt_x)
        plt.xlim([xmin * 10, xmax * 10])

        ax_5 = fig.add_subplot(233)
        plot_signal_sum(ax_5, z=np.arange(0, 12, 1) * LFP_inc,
                        fname=os.path.join(param['result_path'] + path_LFP, 'RecExtElectrode_sum.h5'),
                        unit='mV', T=(xmin, xmax))
        plt.subplots_adjust(hspace=0.5)

    else:
        fig = plt.figure(figsize=(9.5, 4))
        ax3 = fig.add_subplot(231)
        for i in range(spikes_ex[0].shape[0]):
            ax3.plot(spikes_ex[1][i] - begin, np.repeat(spikes_ex[0][i], spikes_ex[1][i].shape[0]), '.b',
                     markersize=size_neurons)
        for i in range(spikes_in[0].shape[0]):
            ax3.plot(spikes_in[1][i] - begin, np.repeat(spikes_in[0][i], spikes_in[1][i].shape[0]), '.r',
                     markersize=size_neurons)
        ax3.set_xlabel('Time (ms)')
        ax3.set_ylabel('Neuron index')

        ax4 = fig.add_subplot(232)
        ax4.plot(TimBinned_ex, popRate_ex, 'b', label='excitatory population')
        ax4.plot(TimBinned_in, popRate_in, 'r', label='inhibitory population')
        ax4.set_xlabel('Time (ms)')
        ax4.set_ylabel('FR')
        ax4.legend()

        plt.subplot(413)
        plt.plot(hist_ex, 'b')
        plt.title('Instantaneous firing rate of excitatory population')
        plt.xlabel('time in ms')
        plt.ylabel('Instantaneous firing rate \nin Hz')
        plt.gca().xaxis.set_major_formatter(format_hixt_x)
        plt.subplot(414)
        plt.plot(hist_in, 'r')
        plt.title('Instantaneous firing rate of inhibitory population')
        plt.xlabel('time in ms')
        plt.ylabel('Instantaneous firing rate \nin Hz')
        plt.gca().xaxis.set_major_formatter(format_hixt_x)

        ax_5 = fig.add_subplot(233)
        plot_signal_sum(ax_5, z=np.arange(0, 12, 1) * LFP_inc,
                        fname=os.path.join(param['result_path'] + path_LFP, 'LFPsum.h5'),
                        unit='mV', T=(begin, end))
        plt.subplots_adjust(hspace=0.5)
    fig.suptitle(param['result_path'])


if __name__ == '__main__':
    import os
    from analyse.get_data import get_data_all

    path_global = os.path.dirname(os.path.realpath(__file__))
    pathes = [
        path_global + '/../data/local_cluster/case_asynchronous',
    ]
    for path in pathes:
        data = get_data_all(path + '/nest/')
        param = {}
        param['param_nest'] = {}
        param['param_nest']["sim_resolution"] = 0.1
        param['param_tvb_model'] = {}
        param['param_tvb_model']['T'] = 20.0
        param['param_nest_topology'] = {}
        param['param_nest_topology']["percentage_inhibitory"] = 0.2
        param['param_nest_topology']["nb_neuron_by_region"] = 10000
        param['result_path'] = path
        print_nest_pop(param, 0.0, 61000.0, data['pop_1_ex'], data['pop_1_in'],
                       V_ex=data['VM_pop_1_ex'], V_in=data['VM_pop_1_in'],
                       W_ex=data['W_pop_1_ex'], W_in=data['W_pop_1_in'],
                       path_LFP='/LFPY/v1/pop_1_/', LFP_inc=70,
                       # xmin=3650,xmax=3750
                       )
        # print_nest_pop(param, 0.0, 61000.0, data['pop_1_ex'], data['pop_1_in'],
        #                path_LFP='/LFPY/v2/pop_1_/',
        #                )
    plt.show()
