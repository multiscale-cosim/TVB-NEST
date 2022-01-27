#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import copy

import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
from matplotlib.text import Text
from scipy import signal
from example.analyse.LFPY.example_plotting import plot_signal_sum
from example.analyse.get_data import get_data_all

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


def print_figure_micro_one(param, begin, end, spikes_ex, spikes_in,
                          V_excitatory=None, V_inhibitory=None, W_excitatory=None, W_inhibitory=None,
                          size_neurons=0.1, spectogram=None, path_LFP='.', LFP_inc=300.0, LFP_start=0.0,
                          grid=None, nb_grid=0, fig=None, font_ticks_size=7, font_labels={'size': 7},
                          labelpad_hist_incr=0):
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
    :param grid: grid where to plot the result
    :param nb_grid: the position along this grid to plot the result
    :param fig: figure of the plot
    :param font_ticks_size: font size of the ticks and label
    :param font_labels: font of labels
    :param labelpad_hist_incr: pad for the label of the histogram
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
    NFFT = int(FS)
    noverlap = int(NFFT / 2)
    vmin = spectogram['DBmin']
    vmax = spectogram['DBmax']
    fmin = spectogram['fmin']
    fmax = spectogram['fmax']
    nb_f = spectogram['nb_f']
    data = (hist_ex + hist_in) / np.max(hist_ex + hist_in)
    data = data[data.shape[0] - int(int(data.shape[0] / NFFT) * NFFT):]
    freqs, psd = signal.welch(data, FS, nfft=NFFT, nperseg=NFFT, noverlap=noverlap, detrend='constant')

    # preparation figure
    if fig is None:
        fig = plt.figure(figsize=(20, 20))
        # plt.suptitle(title)
    if grid is None:
        grid = gridspec.GridSpec(3, 3, figure=fig)
    else:
        grid = gridspec.GridSpecFromSubplotSpec(3, 3, subplot_spec=grid[nb_grid, 0], hspace=0.25)

    grid_neuron = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=grid[:2, 0], hspace=0.001)
    ax_V = fig.add_subplot(grid_neuron[0, 0])
    ax_W = fig.add_subplot(grid_neuron[1, 0])
    grid_last = gridspec.GridSpecFromSubplotSpec(1, 90, subplot_spec=grid[2, :])
    ax_LFP = fig.add_subplot(grid_last[0, :21])
    grid_spike = gridspec.GridSpecFromSubplotSpec(7, 1, subplot_spec=grid[:2, 1:], hspace=0.01)
    ax_spike_train = fig.add_subplot(grid_spike[:3, 0])
    ax_hist_ex = fig.add_subplot(grid_spike[3:5, 0])
    ax_hist_in = fig.add_subplot(grid_spike[5:, 0])
    ax_frequency_1 = fig.add_subplot(grid_last[0, 30:35])
    ax_frequency_2 = fig.add_subplot(grid_last[0, 35:85])

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
    ax_V.set_ylabel('V in (mV)', labelpad=-1, fontdict=font_labels)
    ax_V.spines["right"].set_visible(False)
    ax_V.yaxis.set_ticks_position('left')
    ax_V.spines["bottom"].set_visible(False)
    ax_V.spines["top"].set_visible(False)
    ax_V.xaxis.set_ticks_position('bottom')
    plt.setp(ax_V.get_xticklabels(), visible=False)
    ax_V.locator_params(axis='x', nbins=5)
    ax_V.get_yticklabels()[0].set_visible(False)
    ax_V.tick_params(axis='both', labelsize=font_ticks_size)

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
    if nb_grid == 0:
        ax_W.set_ylabel('W in (pA)', labelpad=3, fontdict=font_labels)
    else:
        ax_W.set_ylabel('W in (pA)', labelpad=0, fontdict=font_labels)
    ax_W.set_xlabel('Time (ms)', fontdict=font_labels)
    ax_W.set_xlim([begin, end])
    ax_W.spines["right"].set_visible(False)
    ax_W.yaxis.set_ticks_position('left')
    ax_W.locator_params(axis='x', nbins=5)
    ax_W.xaxis.set_ticks_position('bottom')
    ax_W.tick_params(axis='both', labelsize=font_ticks_size)

    @ticker.FuncFormatter
    def format_hist(x, pos):
        s = '{}'.format(x)
        return s

    ax_W.xaxis.set_major_formatter(format_hist)
    fig.canvas.draw()
    # LFP
    z = np.ones(32) * (LFP_inc * 15)
    z[10:22] = np.arange(0, 12, 1) + 0.1
    plot_signal_sum(ax_LFP, z=z * LFP_inc,
                    fname=os.path.join(param['result_path'] + path_LFP, 'RecExtElectrode_sum.h5'),
                    unit='mV', T=(LFP_start, LFP_start + end - begin),
                    scalebar_font={'size': font_ticks_size}, modulelabel=2)

    def format_LFP(shift):
        def numfmt(x, pos):
            s = '{}'.format(shift + x)
            return s

        return ticker.FuncFormatter(numfmt)

    ax_LFP.xaxis.set_major_formatter(format_LFP(begin - LFP_start))
    ax_LFP.set_xlabel('Time (ms)', labelpad=2, fontdict=font_labels)
    ax_LFP.set_ylim(ymax=11.3 * LFP_inc)
    ax_LFP.set_xticks([ax_W.xaxis.get_major_ticks()[i].get_loc() - begin + LFP_start for i in
                       range(1, len(ax_W.xaxis.get_major_ticks()) - 1)])
    ax_LFP.tick_params(axis='both', labelsize=font_ticks_size)

    # spike_train
    for i in range(spikes_ex[0].shape[0]):
        ax_spike_train.plot(spikes_excitatory[i], np.repeat(spikes_ex[0][i], spikes_excitatory[i].shape[0]), '.r',
                            markersize=size_neurons)
    for i in range(spikes_in[0].shape[0]):
        ax_spike_train.plot(spikes_inhibitory[i], np.repeat(spikes_in[0][i], spikes_inhibitory[i].shape[0]), '.b',
                            markersize=size_neurons)
    ax_spike_train.set_ylabel('   Neuron index', fontdict=font_labels, labelpad=2+labelpad_hist_incr)
    ax_spike_train.set_xlim([begin - 100, end + 100])
    ax_spike_train.spines["top"].set_visible(False)
    ax_spike_train.spines["right"].set_visible(False)
    ax_spike_train.yaxis.set_ticks_position('left')
    ax_spike_train.xaxis.set_ticks_position('bottom')
    ax_spike_train.get_yticklabels()[0].set_visible(False)
    plt.setp(ax_spike_train.get_xticklabels(), visible=False)
    ax_spike_train.tick_params(axis='both', labelsize=font_ticks_size)
    ax_spike_train.ticklabel_format(axis='y', style="scientific", scilimits=[3, 3])
    ax_spike_train.yaxis.get_offset_text().set_fontsize(font_ticks_size)

    # histogram
    ax_hist_ex.plot(time_array + begin, hist_ex, 'r', linewidth=0.1)
    ax_hist_ex.set_ylabel('IFR (Hz)', fontdict=font_labels, labelpad=2)
    ax_hist_ex.set_xlim([begin - 100, end + 100])
    ax_hist_ex.spines["top"].set_visible(False)
    ax_hist_ex.spines["right"].set_visible(False)
    ax_hist_ex.yaxis.set_ticks_position('left')
    ax_hist_ex.xaxis.set_ticks_position('bottom')
    plt.setp(ax_hist_ex.get_xticklabels(), visible=False)
    ax_hist_ex.get_yticklabels()[0].set_visible(False)
    ax_hist_ex.tick_params(axis='both', labelsize=font_ticks_size)
    ax_hist_ex.locator_params(axis='y', nbins=4)
    ax_hist_in.plot(time_array + begin, hist_in, 'b', linewidth=0.1)
    ax_hist_in.set_xlabel('Time (ms)', fontdict=font_labels, labelpad=2)
    ax_hist_in.set_ylabel('IFR (Hz)', fontdict=font_labels, labelpad=2-labelpad_hist_incr)
    ax_hist_in.set_xlim([begin - 100, end + 100])
    ax_hist_in.spines["top"].set_visible(False)
    ax_hist_in.spines["right"].set_visible(False)
    ax_hist_in.yaxis.set_ticks_position('left')
    ax_hist_in.xaxis.set_ticks_position('bottom')
    ax_hist_in.locator_params(axis='y', nbins=4)

    @ticker.FuncFormatter
    def format_hist(x, pos):
        s = '{}'.format(x * 1.0)
        return s

    ax_hist_in.xaxis.set_major_formatter(format_hist)
    ax_hist_in.tick_params(axis='both', labelsize=font_ticks_size)

    # spectogram
    spectogram_plot = ax_frequency_2.specgram(data, Fs=FS, NFFT=NFFT, noverlap=noverlap, detrend='mean', vmin=vmin,
                                              vmax=vmax, cmap='viridis')
    position_axis = ax_frequency_2.get_subplotspec().get_position(fig).bounds
    cax = plt.axes(
        [position_axis[2] + position_axis[0] + 0.01, position_axis[1], 0.02, position_axis[3]])
    cb = plt.colorbar(spectogram_plot[-1], cax=cax)
    cb.set_label('power spectral density (DB)', fontdict=font_labels)
    cb.ax.tick_params(axis='y', labelsize=font_ticks_size)
    cb.ax.locator_params(axis='y', nbins=4)
    ax_frequency_2.set_ylim(ymax=fmax, ymin=fmin)

    # FuncFormatter can be used as a decorator
    @ticker.FuncFormatter
    def major_formatter(x, pos):
        return "%.1f" % (x * 1e3 + begin)

    ax_frequency_2.xaxis.set_major_formatter(major_formatter)
    ax_frequency_2.set_xlabel('Time (ms)', fontdict=font_labels, labelpad=2)
    ax_frequency_2.get_yaxis().set_visible(False)
    ax_frequency_2.tick_params(axis='both')
    ax_frequency_2.set_xlim([0.1, (end - begin) * 1e-3])
    ax_frequency_2.set_xticks([(ax_hist_in.xaxis.get_major_ticks()[i].get_loc()) * 10 for i in
                               range(1, len(ax_hist_in.xaxis.get_major_ticks()) - 2)])
    ax_frequency_2.spines["top"].set_visible(False)
    ax_frequency_2.spines["right"].set_visible(False)
    ax_frequency_2.yaxis.set_ticks_position('left')
    ax_frequency_2.xaxis.set_ticks_position('bottom')
    ax_frequency_2.tick_params(axis='both', labelsize=font_ticks_size)

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
    ax_frequency_1.set_ylabel('Frequency (Hz)', fontdict=font_labels, labelpad=2)
    ax_frequency_1.vlines(x=10 * np.log10(psd[np.argmax(psd)]),
                          ymin=fmin,
                          ymax=freqs[np.argmax(psd)],
                          color='r',
                          linestyle='--')
    position = [vmin + 5, 10 * np.log10(psd[np.argmax(psd)])]
    position_label = [vmin + 5,  str(np.around(10 * np.log10(psd[np.argmax(psd)]), 1))]
    ax_frequency_1.set_xticklabels(position_label)
    ax_frequency_1.set_xticks(position)
    ax_frequency_1.get_xticklabels()[-1].set_color('r')
    ax_frequency_1.set_xlabel('power spectral density (DB)', fontdict=font_labels, labelpad=2)
    ax_frequency_1.tick_params(axis='both')
    ax_frequency_1.yaxis.set_ticks_position('both')
    ax_frequency_1.xaxis.set_ticks_position('bottom')
    ax_frequency_1.tick_params(axis='both', labelsize=font_ticks_size)
    print(freqs[np.argmax(psd)], psd[np.argmax(psd)])


def print_figure_micro(parameters, begin, end, labelpad_hist_incr, size_neurons=0.1,
                      spectogram=None, path_LFP='.', LFP_inc=300.0, LFP_start=0.0
                      ):
    """
    plot of the figure of the paper
    :param parameters: parameter for the getting data
    :param begin: start of plot
    :param end: end of the plot
    :param labelpad_hist_incr: label pads for the histogram
    :param size_neurons: size of the point of spike for neurons
    :param spectogram: parameter for spectogram analysis
    :param path_LFP: path for file of LFP
    :param LFP_inc: space for LFP
    :param LFP_start: start for plotting LFP
    :return:
    """
    fig = plt.figure(figsize=(6.8, 8.56))
    plt.subplots_adjust(top=0.98, bottom=0.05, left=0.06, right=0.95, hspace=0.21, wspace=0.25)
    # plt.suptitle(param['title'])
    grid = gridspec.GridSpec(len(parameters), 1, figure=fig)
    for index, param in enumerate(parameters):
        data = get_data_all(param['result_path'])
        print_figure_micro_one(
            param, begin, end, data['pop_1_ex'], data['pop_1_in'],
            V_excitatory=data['VM_pop_1_ex'], V_inhibitory=data['VM_pop_1_in'],
            W_excitatory=data['W_pop_1_ex'], W_inhibitory=data['W_pop_1_in'],
            size_neurons=size_neurons,
            spectogram=spectogram,
            path_LFP=path_LFP,
            LFP_inc=LFP_inc,
            LFP_start=LFP_start,
            grid=grid,
            nb_grid=index,
            fig=fig,
            labelpad_hist_incr=labelpad_hist_incr[index],
        )
        # plt.show()

    # add letter of the graph
    fig.add_artist(Text(0.01, 0.97, "a", fontproperties={'size': 7}))
    fig.add_artist(Text(0.01, 0.64, "b", fontproperties={'size': 7}))
    fig.add_artist(Text(0.01, 0.32, "c", fontproperties={'size': 7}))
    # plt.show()

    plt.savefig("figure/Nest_figure.pdf", dpi=300)
    plt.savefig("figure/Nest_figure.png", dpi=150)


if __name__ == '__main__':
    param_default = {}
    param_default['param_nest'] = {}
    param_default['param_nest']["sim_resolution"] = 0.1
    param_default['param_tvb_model'] = {}
    param_default['param_tvb_model']['T'] = 20.0
    param_default['param_nest_topology'] = {}
    param_default['param_nest_topology']["percentage_inhibitory"] = 0.2
    param_default['param_nest_topology']["nb_neuron_by_region"] = 10000

    params = []
    param_asynchronous = copy.copy(param_default)
    param_asynchronous['result_path'] = '../local_cluster/case_asynchronous/nest/'
    param_asynchronous['title'] = " Asynchronous network "
    params.append(param_asynchronous)
    param_up_down = copy.copy(param_default)
    param_up_down['result_path'] = '../local_cluster/case_up_down/nest/'
    param_up_down['title'] = " Synchronise network "
    params.append(param_up_down)
    param_regular_burst = copy.copy(param_default)
    # param_regular_burst['result_path'] = '../local_cluster/case_up_down/nest/'
    param_regular_burst['result_path'] = '../local_cluster/case_regular_burst/nest/'
    param_regular_burst['title'] = " Regular Bursting network "
    params.append(param_regular_burst)

    print_figure_micro(params, 42000.0, 53000.0,
                      spectogram={'DBmin': -65,
                                  'DBmax': -25,
                                  'fmin': 0.0,
                                  'fmax': 200.0,
                                  'nb_f': 4,
                                  },
                      path_LFP='../LFPY/v2/pop_1_/',
                      LFP_inc=100.0,
                      LFP_start=500.0,
                      labelpad_hist_incr=[0,0,4]
                      )
