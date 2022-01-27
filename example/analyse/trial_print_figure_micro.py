#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import signal
from nest_elephant_tvb.transformation.transformation_function.rate_spike import slidding_window

if __name__ == '__main__':
    from example.analyse.print_figure_macro import compute_rate
else:
    from .print_figure_macro import compute_rate

np.set_printoptions(linewidth=300, precision=1, threshold=100000)


def bin_array(array, BIN, time_array, N, Dt):
    """
    compute rate and return the result and sliding windows
    :param array: spike trains
    :param BIN: width of the window
    :param time_array: time of histogram
    :param N: number of neurons
    :param Dt: integration time
    :return:
    """
    hist = compute_rate(array, time_array, N, Dt)
    return (slidding_window(time_array, BIN), slidding_window(hist, BIN), hist)


def print_nest_pop(param, begin, end, spikes_ex, spikes_in, V_excitatory=None, V_inhibitory=None, W_excitatory=None,
                   W_inhibitory=None, histogram=True,
                   size_neurons=0.1, spectogram=None):
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
    bin = int(param['param_tvb_model']['T'] * dt)
    nb_in = int(
        param['param_nest_topology']["nb_neuron_by_region"] * param['param_nest_topology']["percentage_inhibitory"])
    nb_ex = int(param['param_nest_topology']["nb_neuron_by_region"] - nb_in)

    total_time = end - begin
    time_array = np.arange(0, total_time + 1 + dt, dt)
    spikes_excitatory = np.array(
        [spikes_ex[1][i][np.where(np.logical_and(spikes_ex[1][i] >= begin, spikes_ex[1][i] <= end))] for i in
         range(spikes_ex[1].shape[0])])
    spikes_inhibitory = np.array(
        [spikes_in[1][i][np.where(np.logical_and(spikes_in[1][i] >= begin, spikes_in[1][i] <= end))] for i in
         range(spikes_in[1].shape[0])])
    V_ex = [
        V_excitatory[0],
        V_excitatory[1][np.where(np.logical_and(V_excitatory[1] > begin, V_excitatory[1] < end))],
        np.array([V_excitatory[2][i][np.where(np.logical_and(V_excitatory[1] > begin, V_excitatory[1] < end))] for i in
                  range(V_excitatory[2].shape[0])])
    ]
    V_in = [
        V_inhibitory[0],
        V_inhibitory[1][np.where(np.logical_and(V_inhibitory[1] > begin, V_inhibitory[1] < end))],
        np.array([V_inhibitory[2][i][np.where(np.logical_and(V_inhibitory[1] > begin, V_inhibitory[1] < end))] for i in
                  range(V_inhibitory[2].shape[0])])
    ]
    W_ex = [
        W_excitatory[0],
        W_excitatory[1][np.where(np.logical_and(W_excitatory[1] > begin, W_excitatory[1] < end))],
        np.array([W_excitatory[2][i][np.where(np.logical_and(W_excitatory[1] > begin, W_excitatory[1] < end))] for i in
                  range(W_excitatory[2].shape[0])])
    ]
    W_in = [
        W_inhibitory[0],
        W_inhibitory[1][np.where(np.logical_and(W_inhibitory[1] > begin, W_inhibitory[1] < end))],
        np.array([W_inhibitory[2][i][np.where(np.logical_and(W_inhibitory[1] > begin, W_inhibitory[1] < end))] for i in
                  range(W_inhibitory[2].shape[0])])
    ]

    TimBinned_ex, popRate_ex, hist_ex = bin_array(np.around(np.concatenate(spikes_excitatory) - begin, 1), bin,
                                                  time_array, nb_ex, dt)
    TimBinned_in, popRate_in, hist_in = bin_array(np.around(np.concatenate(spikes_inhibitory) - begin, 1), bin,
                                                  time_array, nb_in, dt)

    TimBinned_ex += begin
    TimBinned_in += begin

    import matplotlib.ticker as tkr
    def numfmt(x, pos):  # your custom formatter function: divide by 100.0
        s = '{}'.format(x * dt)
        return s

    format_hixt_x = tkr.FuncFormatter(numfmt)

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
            ax3.plot(spikes_excitatory[i], np.repeat(spikes_ex[0][i], spikes_excitatory[i].shape[0]), '.b',
                     markersize=size_neurons)
        for i in range(spikes_in[0].shape[0]):
            ax3.plot(spikes_inhibitory[i], np.repeat(spikes_in[0][i], spikes_inhibitory[i].shape[0]), '.r',
                     markersize=size_neurons)
        ax3.set_xlabel('Time (ms)')
        ax3.set_ylabel('Neuron index')

        ax4 = fig.add_subplot(224)
        ax4.plot(TimBinned_ex, popRate_ex, 'b', label='excitatory population')
        ax4.plot(TimBinned_in, popRate_in, 'r', label='inhibitory population')
        ax4.set_xlabel('Time (ms)')
        ax4.set_ylabel('FR')
        ax4.legend()

        if histogram:
            plt.figure(figsize=(9.5, 4))
            plt.subplot(211)
            plt.plot(time_array + begin, hist_ex, 'b')
            plt.title('Instantaneous firing rate of excitatory population')
            plt.xlabel('time in ms')
            plt.ylabel('Instantaneous firing rate\n in Hz')
            plt.gca().xaxis.set_major_formatter(format_hixt_x)
            plt.subplot(212)
            plt.plot(time_array + begin, hist_in, 'r')
            plt.title('Instantaneous firing rate of inhibitory population')
            plt.xlabel('time in ms')
            plt.ylabel('Instantaneous firing rate \nin Hz')
            plt.gca().xaxis.set_major_formatter(format_hixt_x)
            plt.subplots_adjust(hspace=0.5)
    else:
        fig = plt.figure(figsize=(9.5, 4))
        ax3 = fig.add_subplot(121)
        for i in range(spikes_ex[0].shape[0]):
            ax3.plot(spikes_excitatory[i] - begin, np.repeat(spikes_ex[0][i], spikes_excitatory[i].shape[0]), '.b',
                     markersize=size_neurons)
        for i in range(spikes_inhibitory[0].shape[0]):
            ax3.plot(spikes_inhibitory[i] - begin, np.repeat(spikes_in[0][i], spikes_inhibitory[i].shape[0]), '.r',
                     markersize=size_neurons)
        ax3.set_xlabel('Time (ms)')
        ax3.set_ylabel('Neuron index')

        ax4 = fig.add_subplot(122)
        ax4.plot(TimBinned_ex, popRate_ex, 'b', label='excitatory population')
        ax4.plot(TimBinned_in, popRate_in, 'r', label='inhibitory population')
        ax4.set_xlabel('Time (ms)')
        ax4.set_ylabel('FR')
        ax4.legend()

        if histogram:
            plt.figure(figsize=(9.5, 4))
            plt.subplot(211)
            plt.plot(time_array + begin, hist_ex, 'b')
            plt.title('Instantaneous firing rate of excitatory population')
            plt.xlabel('time in ms')
            plt.ylabel('Instantaneous firing rate \nin Hz')
            plt.gca().xaxis.set_major_formatter(format_hixt_x)
            plt.subplot(212)
            plt.plot(time_array + begin, hist_in, 'r')
            plt.title('Instantaneous firing rate of inhibitory population')
            plt.xlabel('time in ms')
            plt.ylabel('Instantaneous firing rate \nin Hz')
            plt.gca().xaxis.set_major_formatter(format_hixt_x)
            plt.subplots_adjust(hspace=0.5)
    if spectogram is not None:
        FS = 1 / (param['param_nest']["sim_resolution"] * 1e-3)
        NFFT = int(FS)
        noverlap = int(NFFT / 2)
        vmin = spectogram['DBmin']
        vmax = spectogram['DBmax']
        fmin = spectogram['fmin']
        fmax = spectogram['fmax']
        nb_f = spectogram['nb_f']
        nb_v = spectogram['nb_DB']
        data = (hist_ex + hist_in) / np.max(hist_ex + hist_in)
        data = data[data.shape[0] - int(int(data.shape[0] / NFFT) * NFFT):]
        # data = hist_ex / np.max(hist_ex)
        fig = plt.figure(figsize=(20, 20))
        axs = plt.subplot2grid((1, 4), (0, 1), colspan=3, rowspan=1)
        spectogram_plot = axs.specgram(data, Fs=FS, NFFT=NFFT, noverlap=noverlap, detrend='mean', vmin=vmin, vmax=vmax)
        cb = plt.colorbar(spectogram_plot[-1], ax=axs)
        cb.set_label('power spectral density in DB', fontsize=20)
        cb.ax.tick_params(axis='y', labelsize=10)
        axs.set_ylim(ymax=fmax, ymin=fmin)

        # FuncFormatter can be used as a decorator
        @ticker.FuncFormatter
        def major_formatter(x, pos):
            return "%.1f" % (x + begin * 1e-3)

        axs.xaxis.set_major_formatter(major_formatter)
        axs.set_xticks(
            np.linspace(0., (end - begin - 2 * noverlap * dt) * 1e-3, spectogram['nb_time']) + noverlap * 1e-3 * dt)
        axs.set_xlabel('simulation time in ms', fontsize=20)
        axs.get_yaxis().set_visible(False)
        axs.tick_params(axis='both', labelsize=10)

        axs = plt.subplot2grid((1, 4), (0, 0), colspan=1, rowspan=1)
        freqs, psd = signal.welch(data, FS, nfft=NFFT, nperseg=noverlap, detrend='constant')
        axs.plot(10 * np.log10(psd), freqs)
        axs.hlines(y=freqs[np.argmax(psd)],
                   xmin=10 * np.log10(psd[np.argmax(psd)]),
                   xmax=vmax,
                   color='r', linestyle='--')
        # axs.set_xscale('log')
        axs.set_ylim(ymax=fmax, ymin=fmin)
        axs.set_xlim(xmax=vmax, xmin=vmin)
        axs.invert_xaxis()
        position = [i for i in np.linspace(fmin, fmax, nb_f)] + [freqs[np.argmax(psd)]]
        position_label = [str(i) for i in np.linspace(fmin, fmax, nb_f)] + [str(int(freqs[np.argmax(psd)]))]
        axs.set_yticklabels(position_label)
        axs.set_yticks(position)
        axs.get_yticklabels()[-1].set_color('r')
        axs.set_ylabel('Frequency in Hz', fontsize=20)

        axs.vlines(x=10 * np.log10(psd[np.argmax(psd)]),
                   ymin=fmin,
                   ymax=freqs[np.argmax(psd)],
                   color='r',
                   linestyle='--')
        position = [i for i in np.linspace(vmin, vmax, nb_v)] + [10 * np.log10(psd[np.argmax(psd)])]
        position_label = [str(i) for i in np.linspace(vmin, vmax, nb_v)] + [
            str(np.around(10 * np.log10(psd[np.argmax(psd)]), 1))]
        axs.set_xticklabels(position_label)
        axs.set_xticks(position)
        axs.get_xticklabels()[-1].set_color('r')
        axs.set_xlabel('power spectral density in DB', fontsize=20)
        axs.tick_params(axis='both', labelsize=10)
        plt.subplots_adjust(hspace=0.5, wspace=0.1)
        plt.suptitle(spectogram['title_figure'], fontsize=20)
        print(freqs[np.argmax(psd)], psd[np.argmax(psd)])
    plt.show()


def print_spiketrain(begin, end, spikes, size_neurons=0.5):
    """
    plot a spike trains in simple way
    :param begin: start time of plot
    :param end: end time of plot
    :param spikes: spikes train
    :param size_neurons: size of the neurons
    :return:
    """
    plt.figure(figsize=(20, 20))
    for i in range(spikes[0].shape[0]):
        plt.plot(spikes[1][i] - begin, np.repeat(spikes[0][i], spikes[1][i].shape[0]), '.b',
                 markersize=size_neurons)
    # plt.xlabel('Time (ms)')
    # plt.ylabel('Neuron index')
    plt.xticks([-1, -1.00001], ['', ''])
    plt.yticks([-1, -1.000001], ['', ''])
    plt.ylim(ymin=np.min(spikes[0]) - size_neurons, ymax=np.max(spikes[0]) + size_neurons)
    plt.xlim(xmin=begin, xmax=end)
    plt.show()


def print_rate(folder_simulation, begin, end, nb_regions):
    """
    plot rate in simple way
    :param folder_simulation: path of the folder simulation
    :param begin: start of the plot
    :param end: end of the plot
    :param nb_regions: number of region
    :return:
    """
    from example.analyse.get_data import get_rate
    plt.figure(figsize=(20, 20))
    result_raw = get_rate(folder_simulation + '/tvb/')[0]  # result of the Raw monitor

    # separate the different variable
    times = result_raw[0]
    state_variable = np.concatenate(result_raw[1]).reshape((result_raw[1].shape[0], 7,
                                                            nb_regions))  # shape : time, state variable, region
    plt.plot(times, state_variable[:, 1, :] * 1e3)
    # plt.ylabel('firing rate in Hz')
    # plt.xlabel('time in ms')
    # plt.title('firing rate of inhibitory population')
    plt.xticks([-1, -1.00001], ['', ''])
    plt.yticks([-1, -1.000001], ['', ''])
    plt.ylim(ymin=0.0)
    plt.xlim(xmin=begin, xmax=end)

    plt.figure(figsize=(20, 20))
    plt.plot(times, state_variable[:, 0, :10] * 1e3)
    # plt.ylabel('firing rate in Hz')
    # plt.xlabel('time in ms')
    # plt.title('firing rate of excitatory population')
    plt.xticks([-1, -1.00001], ['', ''])
    plt.yticks([-1, -1.000001], ['', ''])
    plt.ylim(ymin=0.0)
    plt.xlim(xmin=begin, xmax=end)
    plt.show()


# Test the function, helping for debugging
if __name__ == '__main__':
    from example.analyse.get_data import get_data_all

    # # Test function fo rate and spike trains
    # data = get_data_all('../local/case_up_down/nest/')
    # print_rate('../local/case_up_down/', 0.0, 2000.0, 104)
    # print_spiketrain(50.0,2000.0,data['pop_1_ex'],10.0)
    # print_spiketrain(30.0,1950.0,data['pop_2_ex'],10.0)

    param = {}
    param['param_nest'] = {}
    param['param_nest']["sim_resolution"] = 0.1
    param['param_tvb_model'] = {}
    param['param_tvb_model']['T'] = 20.0
    param['param_nest_topology'] = {}
    param['param_nest_topology']["percentage_inhibitory"] = 0.2
    param['param_nest_topology']["nb_neuron_by_region"] = 10000
    data = get_data_all('../local/case_asynchronous/nest/'); title = " Asynchronous network "
    # data = get_data_all('../local/case_regular_burst/nest/'); title = " Regular Bursting network "
    # data = get_data_all('../local/case_up_down/nest/'); title = " Synchronise network "
    # print_nest_pop(param, 39500.0, 50500.0, data['pop_1_ex'], data['pop_1_in'],
    print_nest_pop(param, 500.0, 10000.0, data['pop_1_ex'], data['pop_1_in'],
                                  V_excitatory=data['VM_pop_1_ex'], V_inhibitory=data['VM_pop_1_in'],
                   W_excitatory=data['W_pop_1_ex'], W_inhibitory=data['W_pop_1_in'],
                   histogram=True,
                   spectogram={'DBmin': -65,
                               'DBmax': -25,
                               'nb_DB': 3,
                               'fmin': 0.0,
                               'fmax': 200.0,
                               'nb_f': 21,
                               'nb_time': 11,
                               'title_figure': 'Spectrogram of ' + title + ' for 10 s of simulation'
                               })
