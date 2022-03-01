#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker
from cycler import cycler
import numpy as np

from analyse.LFPY.example_plotting import plot_signal_sum
from analyse.get_data import get_data_all, get_rate

np.set_printoptions(linewidth=300, precision=1, threshold=100000)

def print_figure_micro_one(param, begin, end, spikes_ex, spikes_in,
                           V_excitatory=None, V_inhibitory=None, W_excitatory=None, W_inhibitory=None,
                           size_neurons=0.1, path_LFP='.', LFP_inc=300.0, LFP_start=0.0,
                           figsize=(6.8, 8.56), font_ticks_size=7, font_labels={'size': 7},
                           path_fig='figure.pdf'
                           ):
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
    :param path_LFP: path for file of LFP
    :param LFP_inc: space for LFP
    :param figsize: figure size
    :param font_ticks_size: font size of the ticks and label
    :param font_labels: font of labels
    :param path_fig: path for saving the figure
    :return:
    """
    # spikes and histogram
    spikes_excitatory = np.array(
        [spikes_ex[1][i][np.where(np.logical_and(spikes_ex[1][i] >= begin, spikes_ex[1][i] <= end))] for i in
         range(spikes_ex[1].shape[0])])
    spikes_inhibitory = np.array(
        [spikes_in[1][i][np.where(np.logical_and(spikes_in[1][i] >= begin, spikes_in[1][i] <= end))] for i in
         range(spikes_in[1].shape[0])])

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


    # preparation figure
    fig = plt.figure(figsize=figsize)
    grid = gridspec.GridSpec(2, 2, figure=fig)

    ax_V = fig.add_subplot(grid[0, 0])
    ax_W = fig.add_subplot(grid[1, 0])
    ax_LFP = fig.add_subplot(grid[1, 1])
    ax_spike_train = fig.add_subplot(grid[0, 1])

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
    ax_W.set_ylabel('W in (pA)', labelpad=-1, fontdict=font_labels)
    ax_W.set_xlabel('Time (ms)', fontdict=font_labels, labelpad=1)
    ax_W.set_xlim([begin, end])
    ax_W.spines["right"].set_visible(False)
    ax_W.spines["top"].set_visible(False)
    ax_W.yaxis.set_ticks_position('left')
    ax_W.locator_params(axis='x', nbins=5)
    ax_W.xaxis.set_ticks_position('bottom')
    ax_W.tick_params(axis='both', labelsize=font_ticks_size)

    @ticker.FuncFormatter
    def format_hist(x, pos):
        s = '{}'.format(x)
        return s

    ax_W.xaxis.set_major_formatter(format_hist)

    # spike_train
    for i in range(spikes_ex[0].shape[0]):
        ax_spike_train.plot(spikes_excitatory[i], np.repeat(spikes_ex[0][i], spikes_excitatory[i].shape[0]), '.r',
                            markersize=size_neurons)
    for i in range(spikes_in[0].shape[0]):
        ax_spike_train.plot(spikes_inhibitory[i], np.repeat(spikes_in[0][i], spikes_inhibitory[i].shape[0]), '.b',
                            markersize=size_neurons)
    ax_spike_train.set_ylabel('   Neuron index', fontdict=font_labels, labelpad=2)
    ax_spike_train.set_xlim([begin - 100, end + 100])
    ax_spike_train.spines["top"].set_visible(False)
    ax_spike_train.spines["right"].set_visible(False)
    ax_spike_train.yaxis.set_ticks_position('left')
    ax_spike_train.locator_params(axis='x', nbins=5)
    ax_spike_train.xaxis.set_ticks_position('bottom')
    plt.setp(ax_spike_train.get_xticklabels(), visible=False)
    ax_spike_train.tick_params(axis='both', labelsize=font_ticks_size)
    ax_spike_train.ticklabel_format(axis='y', style="scientific", scilimits=[3, 3])
    ax_spike_train.yaxis.get_offset_text().set_fontsize(font_ticks_size)


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




    plt.subplots_adjust(top=0.94, bottom=0.12, left=0.11, right=0.96, hspace=0.21, wspace=0.31)
    plt.savefig(path_fig)


def print_figure_macro_one(param, begin, end, TVB_data,
                           figsize=(20,20),
                           font_ticks_size=7, font_labels={'size': 7},
                           path_fig='./figure.pdf'
                           ):
    """
    print TVB figure
    :param param: parameter of the figure
    :param begin: start of measure
    :param end: en of measure
    :param TVB_data: rate of regions
    :param figsize: figure size
    :param font_ticks_size: font size of the ticks and label
    :param font_labels: font of labels
    :param path_fig: path for saving the figure
    :return:
    """
    # parameter of the simulation
    nb_regions = param['param_nest_topology']['nb_region']

    # rate
    result_raw = TVB_data[0]
    state_times = result_raw[0]
    state_variable = np.concatenate(result_raw[1]).reshape(
        (result_raw[1].shape[0], 7, nb_regions))  # shape : time, state variable, region
    mask = np.where(np.logical_and(state_times < end, state_times > begin))
    state_times = state_times[mask]
    state_variable = state_variable[mask]

    # ECOG
    result_raw = TVB_data[1]
    ECOG_time = result_raw[0]
    ECOG = np.array([i for i in result_raw[1]])[:, 0, :, 0]
    mask = np.where(np.logical_and(ECOG_time < end, ECOG_time > begin))
    ECOG_time = ECOG_time[mask]
    ECOG = ECOG[mask]

    # preparation figure
    fig = plt.figure(figsize=figsize)
    grid = gridspec.GridSpec(1, 2, figure=fig)

    ECOG_1 = fig.add_subplot(grid[0, 0])
    ax_rate = fig.add_subplot(grid[0, 1])

    # print rate
    max_rate = np.nanmax(state_variable[:, 1, :]) * 1e3
    print(max_rate)
    for i in range(nb_regions):
        if i in [26, 78]:
            ax_rate.plot(state_times, state_variable[:, 0, i] * 1e3 + i * max_rate, 'k', linewidth=1.0)
        else:
            ax_rate.plot(state_times, state_variable[:, 0, i] * 1e3 + i * max_rate, 'r', linewidth=0.8)
            ax_rate.plot(state_times, state_variable[:, 1, i] * 1e3 + i * max_rate, 'b', linewidth=00.8)
    position = [i * max_rate + max_rate / 2 for i in
                np.array(np.around(np.linspace(0, nb_regions - 1, 5)), dtype=int)]
    position_label = [i for i in np.array(np.around(np.linspace(0, nb_regions - 1, 5)), dtype=int)]
    ax_rate.set_yticklabels(position_label)
    ax_rate.set_yticks(position)
    ax_rate.set_xlabel('Time (ms)', labelpad=1, fontdict=font_labels)
    ax_rate.set_ylabel('Region Id', labelpad=-4, fontdict=font_labels)
    ax_rate.set_ylim(ymin=-max_rate, ymax=max_rate * (nb_regions + 1.0))
    ax_rate.set_xlim(xmin=begin - 100, xmax=end + 100)
    ax_rate.tick_params(axis='both', labelsize=font_ticks_size)
    ax_rate.locator_params(axis='x', nbins=5)
    ax_rate.spines["top"].set_visible(False)
    ax_rate.spines["right"].set_visible(False)
    ax_rate.yaxis.set_ticks_position('left')
    ax_rate.xaxis.set_ticks_position('bottom')

    # ECOG
    max_ecog = np.nanmax(ECOG[:, :])
    custom_cycler = (cycler(color=plt.cm.jet(np.linspace(0, 1, 7))))
    ECOG_1.set_prop_cycle(custom_cycler)
    for i in range(8):
        ECOG_1.plot(ECOG_time, ECOG[:, i + ECOG.shape[1] // 2] + i * max_ecog, linewidth=0.1)
    ECOG_1.yaxis.set_ticks_position('left')
    plt.setp(ECOG_1.get_xticklabels(), visible=False)
    plt.setp(ECOG_1.get_yticklabels(), visible=False)
    ECOG_1.set_ylabel('set of electrodes left', labelpad=1, fontdict=font_labels)
    ECOG_1.set_xlabel('Time (ms)', labelpad=1, fontdict=font_labels)
    plt.setp(ECOG_1.get_xticklabels(), visible=True)
    ECOG_1.tick_params(axis='x', which='both', left='on',
                       bottom='on', labelbottom='on', length=1.0, labelsize=font_ticks_size)
    ECOG_1.locator_params(axis='x', nbins=5)
    ECOG_1.set_xlim(xmin=begin - 100, xmax=end + 100)
    ECOG_1.set_ylim(ymin=0.0, ymax=max_ecog*8)
    ECOG_1.spines["top"].set_visible(False)
    ECOG_1.spines["right"].set_visible(False)
    ECOG_1.xaxis.set_ticks_position('bottom')

    plt.subplots_adjust(top=0.98, bottom=0.12, left=0.05, right=0.99, hspace=0.21, wspace=0.23)
    plt.savefig(path_fig)


if __name__ == "__main__":
    import os

    path = os.path.dirname(os.path.realpath(__file__))
    param_up_down = {}
    param_up_down['param_nest'] = {}
    param_up_down['param_nest']["sim_resolution"] = 0.1
    param_up_down['param_tvb_model'] = {}
    param_up_down['param_tvb_model']['T'] = 20.0
    param_up_down['param_nest_topology'] = {}
    param_up_down['param_nest_topology']["percentage_inhibitory"] = 0.2
    param_up_down['param_nest_topology']["nb_neuron_by_region"] = 10000
    param_up_down['result_path'] = path+'/../data/local_cluster/case_up_down/nest/'
    param_up_down['title'] = " Synchronise network "
    data = get_data_all(param_up_down['result_path'])
    print_figure_micro_one(
            param_up_down, 42000.0, 53000.0, data['pop_1_ex'], data['pop_1_in'],
            V_excitatory=data['VM_pop_1_ex'], V_inhibitory=data['VM_pop_1_in'],
            W_excitatory=data['W_pop_1_ex'], W_inhibitory=data['W_pop_1_in'],
            size_neurons=0.1,
            path_LFP='../LFPY/v2/pop_1_/',
            LFP_inc=300.0,
            LFP_start=0.0,
            figsize=(3.47, 2.57),
            path_fig=path+'/../data/figure/fig_2_neuron_activity.pdf'
        )

    param_regular_burst = {}
    param_regular_burst['param_nest'] = {}
    param_regular_burst['param_nest']["sim_resolution"] = 0.1
    param_regular_burst['param_tvb_model'] = {}
    param_regular_burst['param_tvb_model']['T'] = 20.0
    param_regular_burst['param_nest_topology'] = {}
    param_regular_burst['param_nest_topology']["percentage_inhibitory"] = 0.2
    param_regular_burst['param_nest_topology']["nb_neuron_by_region"] = 10000
    param_regular_burst['param_nest_topology']["nb_region"] = 104
    param_regular_burst['result_path'] = path+'/../data/local_cluster/case_regular_burst/'
    param_regular_burst['title'] = " Regular Bursting network "

    # paper figure
    rates = get_rate(param_regular_burst['result_path'] + '/tvb/')
    rates[1] = np.load(param_regular_burst['result_path'] + '/tvb/ECOG.npy', allow_pickle=True)
    print_figure_macro_one(param_regular_burst, 42500.0, 53500.0, rates, figsize=(3.47, 2.57),
                           path_fig=path+'/../data/figure/fig_2_brain_activity.pdf')





