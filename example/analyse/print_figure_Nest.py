#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
from scipy import signal
import matplotlib.ticker as tkr
# from example.analyse.LFPY.example_plotting import plot_signal_sum

np.set_printoptions(linewidth=300, precision=1, threshold=100000)


def compute_rate(data, time, N, Dt):
    """
    Compute the firing rate
    :param data: the spike of all neurons between end and begin
    :param time: time of the plot
    :param N: number of neurons
    :param Dt: resolution of the simulation
    :return: the mean and the standard deviation of firing rate, the maximum and minimum of firing rate
    """
    # get data
    n_fil = np.searchsorted(time, data)
    n_fil = n_fil.astype(int)
    # count the number of the same id
    count_of_t = np.bincount(n_fil)
    # compute the rate
    rate_each_t_incomplet = count_of_t / float(N)
    rate_each_t = np.concatenate(
        (rate_each_t_incomplet, np.zeros(len(time) - np.shape(rate_each_t_incomplet)[0])))
    return rate_each_t / (Dt * 1e-3)


def print_figure_nest(param, begin, end, spikes_ex, spikes_in,
                      V_excitatory=None, V_inhibitory=None, W_excitatory=None, W_inhibitory=None,
                      size_neurons=0.1, spectogram=None, path_LFP='.', LFP_inc=300.0):
    """
    print the result of Nest
    :param param: the parameter of the simulation
    :param begin: begging of the measure of the simulation
    :param end: end of the measure of the simulation
    :param spikes_ex: spikes of excitatory neurons
    :param spikes_in: spikes of inhibitory neurons
    :param V_excitatory: voltage of excitatory neurons
    :param V_inhibitory: voltage of inhibitory neurons
    :param W_excitatory: adaptation of excitatory neurons
    :param W_inhibitory: adaptation of inhibitory neurons
    :param size_neurons: size of the point of spike for neurons
    :param spectogram: parameter for spectogram analysis
    :param path_LFP: path for file of LFP
    :param LFP_inc: space for LFP
    :return:
    """
    # parameter of the simulation
    dt = param['param_nest']["sim_resolution"]
    nb_in = int(
        param['param_nest_topology']["nb_neuron_by_region"] * param['param_nest_topology']["percentage_inhibitory"])
    nb_ex = int(param['param_nest_topology']["nb_neuron_by_region"] - nb_in)

    # time
    total_time = end - begin
    time_array = np.arange(0, total_time + 1 + dt, dt)

    # spikes and histogram
    spikes_excitatory = np.array(
        [spikes_ex[1][i][np.where(np.logical_and(spikes_ex[1][i] >= begin, spikes_ex[1][i] <= end))] for i in
         range(spikes_ex[1].shape[0])])
    spikes_inhibitory = np.array(
        [spikes_in[1][i][np.where(np.logical_and(spikes_in[1][i] >= begin, spikes_in[1][i] <= end))] for i in
         range(spikes_in[1].shape[0])])
    hist_ex = compute_rate(np.around(np.concatenate(spikes_excitatory) - begin, 1), time_array, nb_ex, dt)
    hist_in = compute_rate(np.around(np.concatenate(spikes_inhibitory) - begin, 1), time_array, nb_in, dt)

    # voltage membrane and adaptation
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

    # Frequency analysis of histogram
    FS = 1 / (param['param_nest']["sim_resolution"] * 1e-3)
    FS = 1
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
    freqs, psd = signal.welch(data, FS, nfft=NFFT, nperseg=NFFT, noverlap=noverlap, detrend='constant')

    # preparation figure
    fig = plt.figure(figsize=(20, 20))
    # plt.suptitle(title)
    grid = gridspec.GridSpec(3, 3, figure=fig)
    grid_neuron = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=grid[:2, 0], hspace=0.001)
    ax_V = fig.add_subplot(grid_neuron[0, 0])
    ax_W = fig.add_subplot(grid_neuron[1, 0])
    grid_last = gridspec.GridSpecFromSubplotSpec(1, 90, subplot_spec=grid[2, :])
    ax_LFP = fig.add_subplot(grid_last[0, :21])
    grid_spike = gridspec.GridSpecFromSubplotSpec(4, 1, subplot_spec=grid[:2, 1:], hspace=0.01)
    ax_spike_train = fig.add_subplot(grid_spike[:2, 0])
    ax_hist_ex = fig.add_subplot(grid_spike[2, 0])
    ax_hist_in = fig.add_subplot(grid_spike[3, 0])
    ax_frequency_1 = fig.add_subplot(grid_last[0, 27:32])
    ax_frequency_2 = fig.add_subplot(grid_last[0, 32:])

    # Voltage
    for a in range(10):
        ax_V.plot(V_ex[1], V_ex[2][a], 'r:', linewidth=0.1, alpha=0.1)
        ax_V.plot(V_in[1], V_in[2][a], 'b:', linewidth=0.1, alpha=0.1)
    ax_V.plot(time_V_ex, mean_V_ex, 'r', linewidth=1.0)
    ax_V.plot(time_V_ex, max_V_ex, 'r--', linewidth=0.1)
    ax_V.plot(time_V_ex, min_V_ex, 'r--', linewidth=0.1)
    ax_V.plot(time_V_in, mean_V_in, 'b', linewidth=1.0)
    ax_V.plot(time_V_in, max_V_in, 'b--', linewidth=0.1)
    ax_V.plot(time_V_in, min_V_in, 'b--', linewidth=0.1)
    ax_V.set_ylim([-90, -30])
    ax_V.set_xlim([begin, end])
    ax_V.set_ylabel('V in (mV)')
    ax_V.spines["right"].set_visible(False)
    ax_V.yaxis.set_ticks_position('left')
    ax_V.spines["bottom"].set_visible(False)
    ax_V.spines["top"].set_visible(False)
    ax_V.xaxis.set_ticks_position('bottom')
    plt.setp(ax_V.get_xticklabels(), visible=False)
    ax_V.get_yticklabels()[0].set_visible(False)

    # Adaptation
    for a in range(10):
        ax_W.plot(W_ex[1], W_ex[2][a], 'r:', linewidth=0.1, alpha=0.1)
        ax_W.plot(W_in[1], W_in[2][a], 'b:', linewidth=0.1, alpha=0.1)
    ax_W.plot(time_W_ex, mean_W_ex, 'r', linewidth=1.0)
    ax_W.plot(time_W_ex, max_W_ex, 'r--', linewidth=0.1)
    ax_W.plot(time_W_ex, min_W_ex, 'r--', linewidth=0.1)
    ax_W.plot(time_W_in, mean_W_in, 'b', linewidth=1.0)
    ax_W.plot(time_W_in, max_W_in, 'b--', linewidth=0.1)
    ax_W.plot(time_W_in, min_W_in, 'b--', linewidth=0.1)
    ax_W.set_ylabel('W in (pA)')
    ax_W.set_xlabel('Time (ms)')
    ax_W.set_xlim([begin, end])
    ax_W.spines["right"].set_visible(False)
    ax_W.yaxis.set_ticks_position('left')
    ax_W.xaxis.set_ticks_position('bottom')

    @ticker.FuncFormatter
    def format_hist(x, pos):
        s = '{}'.format(x)
        return s

    ax_W.xaxis.set_major_formatter(format_hist)

    # LFP
    # plot_signal_sum(ax_LFP, z=np.arange(0,12,1)*LFP_inc,
    #                 fname=os.path.join(param['result_path']+path_LFP, 'LFPsum.h5'),
    #                 unit='mV', T=(0,11000))
    # def format_LFP(shift):
    #     def numfmt(x, pos):
    #         s = '{}'.format(shift + x)
    #         return s
    #     return tkr.FuncFormatter(numfmt)
    # ax_LFP.xaxis.set_major_formatter(format_LFP(begin))
    # ax_LFP.set_xlabel('Time (ms)',labelpad=ax_frequency_2.get_xaxis().labelpad)

    # spike_train
    for i in range(spikes_ex[0].shape[0]):
        ax_spike_train.plot(spikes_excitatory[i], np.repeat(spikes_ex[0][i], spikes_excitatory[i].shape[0]), '.r',
                            markersize=size_neurons)
    for i in range(spikes_in[0].shape[0]):
        ax_spike_train.plot(spikes_inhibitory[i], np.repeat(spikes_in[0][i], spikes_inhibitory[i].shape[0]), '.b',
                            markersize=size_neurons)
    ax_spike_train.set_ylabel('Neuron index')
    ax_spike_train.set_xlim([begin - 100, end + 100])
    ax_spike_train.spines["top"].set_visible(False)
    ax_spike_train.spines["right"].set_visible(False)
    ax_spike_train.yaxis.set_ticks_position('left')
    ax_spike_train.xaxis.set_ticks_position('bottom')
    ax_spike_train.get_yticklabels()[0].set_visible(False)
    plt.setp(ax_spike_train.get_xticklabels(), visible=False)

    # histogram
    ax_hist_ex.plot(time_array + begin, hist_ex, 'r', linewidth=0.1)
    ax_hist_ex.set_ylabel('IFR (Hz)\n')
    ax_hist_ex.set_xlim([begin - 100, end + 100])
    ax_hist_ex.spines["top"].set_visible(False)
    ax_hist_ex.spines["right"].set_visible(False)
    ax_hist_ex.yaxis.set_ticks_position('left')
    ax_hist_ex.xaxis.set_ticks_position('bottom')
    plt.setp(ax_hist_ex.get_xticklabels(), visible=False)
    ax_hist_ex.get_yticklabels()[0].set_visible(False)
    ax_hist_in.plot(time_array + begin, hist_in, 'b', linewidth=0.1)
    ax_hist_in.set_xlabel('Time (ms)')
    ax_hist_in.set_ylabel('IFR (Hz)\n')
    ax_hist_in.set_xlim([begin - 100, end + 100])
    ax_hist_in.spines["top"].set_visible(False)
    ax_hist_in.spines["right"].set_visible(False)
    ax_hist_in.yaxis.set_ticks_position('left')
    ax_hist_in.xaxis.set_ticks_position('bottom')

    @ticker.FuncFormatter
    def format_hist(x, pos):
        s = '{}'.format(x * 1.0)
        return s

    ax_hist_in.xaxis.set_major_formatter(format_hist)

    # spectogram
    spectogram_plot = ax_frequency_2.specgram(data, Fs=FS, NFFT=NFFT, noverlap=noverlap, detrend='mean', vmin=vmin,
                                              vmax=vmax, cmap='viridis')
    cax = plt.axes(
        [ax_frequency_2.figbox.bounds[2] + ax_frequency_2.figbox.bounds[0] + 0.01, ax_frequency_2.figbox.bounds[1],
         0.02, ax_frequency_2.figbox.bounds[3]])
    cb = plt.colorbar(spectogram_plot[-1], cax=cax)
    cb.set_label('power spectral density (DB)')
    cb.ax.tick_params(axis='y')
    ax_frequency_2.set_ylim(ymax=fmax, ymin=fmin)

    # FuncFormatter can be used as a decorator
    @ticker.FuncFormatter
    def major_formatter(x, pos):
        return "%.1f" % (x * 1e3 + begin)

    ax_frequency_2.xaxis.set_major_formatter(major_formatter)
    ax_frequency_2.set_xlabel('Time (ms)')
    ax_frequency_2.get_yaxis().set_visible(False)
    ax_frequency_2.tick_params(axis='both')
    ax_frequency_2.set_xlim([0.1, (end - begin) * 1e-3])
    ax_frequency_2.spines["top"].set_visible(False)
    ax_frequency_2.spines["right"].set_visible(False)
    ax_frequency_2.yaxis.set_ticks_position('left')
    ax_frequency_2.xaxis.set_ticks_position('bottom')

    # spectogram concatenate
    ax_frequency_1.plot(10 * np.log10(psd), freqs)
    ax_frequency_1.hlines(y=freqs[np.argmax(psd)],
                          xmin=10 * np.log10(psd[np.argmax(psd)]),
                          xmax=vmax,
                          color='r', linestyle='--')
    ax_frequency_1.set_ylim(ymax=fmax, ymin=fmin)
    ax_frequency_1.set_xlim(xmax=vmax, xmin=vmin)
    ax_frequency_1.invert_xaxis()
    position = [i for i in np.linspace(fmin + 50, fmax, nb_f)] + [freqs[np.argmax(psd)]]
    position_label = [str(i) for i in np.linspace(fmin + 50, fmax, nb_f)] + [str(int(freqs[np.argmax(psd)]))]
    ax_frequency_1.set_yticklabels(position_label)
    ax_frequency_1.set_yticks(position)
    ax_frequency_1.get_yticklabels()[-1].set_color('r')
    ax_frequency_1.set_ylabel('Frequency (Hz)')
    ax_frequency_1.vlines(x=10 * np.log10(psd[np.argmax(psd)]),
                          ymin=fmin,
                          ymax=freqs[np.argmax(psd)],
                          color='r',
                          linestyle='--')
    position = [vmin + 5, vmax, 10 * np.log10(psd[np.argmax(psd)])]
    position_label = [vmin + 5, vmax, str(np.around(10 * np.log10(psd[np.argmax(psd)]), 1))]
    ax_frequency_1.set_xticklabels(position_label)
    ax_frequency_1.set_xticks(position)
    ax_frequency_1.get_xticklabels()[-1].set_color('r')
    ax_frequency_1.set_xlabel('power spectral density (DB)')
    ax_frequency_1.tick_params(axis='both')
    ax_frequency_1.yaxis.set_ticks_position('both')
    ax_frequency_1.xaxis.set_ticks_position('bottom')
    print(freqs[np.argmax(psd)], psd[np.argmax(psd)])

    plt.show()


if __name__ == '__main__':
    from example.analyse.get_data import get_data_all

    param = {}
    param['param_nest'] = {}
    param['param_nest']["sim_resolution"] = 0.1
    param['param_tvb_model'] = {}
    param['param_tvb_model']['T'] = 20.0
    param['param_nest_topology'] = {}
    param['param_nest_topology']["percentage_inhibitory"] = 0.2
    param['param_nest_topology']["nb_neuron_by_region"] = 10000
    # param['result_path'] = '../local/case_up_down/nest/'; title = " Synchronise network "
    # param['result_path'] ='../local/case_asynchronous/nest/'; title = " Asynchronous network "
    # param['result_path'] = '../local/case_regular_burst/nest/'; title = " Regular Bursting network "
    # param['result_path'] = '../piz_daint/sarus/v1/case_asynchronous/nest/'; title = " Regular Bursting network "
    # param['result_path'] = '../piz_daint/sarus/v1/case_regular_burst/nest/'; title = " Regular Bursting network "
    # param['result_path'] = '../piz_daint/sarus/v1/case_up_down/nest/'; title = " Synchronise network "
    # param['result_path'] = '../singularity/case_up_down/nest/'; title = " Synchronise network "
    # param['result_path'] = '../docker/case_up_down/nest/'; title = " Synchronise network "
    # param['result_path'] = '../singularity/case_asynchronous/nest/'; title = " Asynchronous network "
    # param['result_path'] = '../docker/case_asynchronous/nest/'; title = " Asynchronous network "
    # param['result_path'] = '../singularity/case_regular_burst/nest/'; title = " Regular Bursting network "
    param['result_path'] = '../docker/case_regular_burst/nest/'; title = " Regular Bursting network "
    data = get_data_all(param['result_path'])
    # print_figure_nest(param, 49000.0, 60000.0,data['pop_1_ex'],data['pop_1_in'],
    # print_figure_nest(param, 6000.0, 10000.0, data['pop_1_ex'], data['pop_1_in'],
    print_figure_nest(param, 0.0, 200.0, data['pop_1_ex'], data['pop_1_in'],
                                        V_excitatory=data['VM_pop_1_ex'], V_inhibitory=data['VM_pop_1_in'],
                      W_excitatory=data['W_pop_1_ex'], W_inhibitory=data['W_pop_1_in'],
                      spectogram={'DBmin': -65,
                                  'DBmax': -25,
                                  'nb_DB': 3,
                                  'fmin': 0.0,
                                  'fmax': 200.0,
                                  'nb_f': 4,
                                  'nb_time': 11,
                                  'title_figure': 'Spectrogram of ' + title + ' for 10 s of simulation'
                                  },
                      # path_LFP='../LFPY/small_init_test_2/small_pop_1/',
                      # LFP_inc=150.0
                      )
