#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as tkr
from matplotlib.text import Text
from cycler import cycler
import copy

from nest_elephant_tvb.transformation.transformation_function.rate_spike import slidding_window
from example.analyse.get_data import get_data_all, get_rate

np.set_printoptions(linewidth=300, precision=1, threshold=100000)


def format_hist(dt):
    """
    format for label of x axis of histogram
    :param dt: time step
    :return:
    """

    def numfmt(x, pos):  # your custom formatter function: divide by 100.0
        s = '{}'.format(x * dt)
        return s

    return tkr.FuncFormatter(numfmt)


def compute_rate(data, time, N, Dt):
    """
    Compute the firing rate
    :param data: the spike of all neurons between end and begin
    :param time: time of the simulation
    :param N: number of neurons
    :param Dt: time step
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
    return slidding_window(time_array, BIN), slidding_window(hist, BIN), hist


def print_figure_macro_one(param, begin, end, spikes_ex, spikes_in, TVB_data,
                         grid=None, nb_grid=0, fig=None,
                         font_ticks_size=7, font_labels={'size': 7}
                         ):
    """
    print TVB figure
    :param param: parameter of the figure
    :param begin: start of measure
    :param end: en of measure
    :param spikes_ex: spike of excitaotry neurons
    :param spikes_in: spikes of inhibitory neurons
    :param TVB_data: rate of regions
    :param grid: grid where to plot the result
    :param nb_grid: the position along this grid to plot the result
    :param fig: figure of the plot
    :param font_ticks_size: font size of the ticks and label
    :param font_labels: font of labels
    :return:
    """
    # parameter of the simulation
    dt = param['param_nest']["sim_resolution"]
    nb_regions = param['param_nest_topology']['nb_region']
    bin = int(param['param_tvb_model']['T'] / dt)
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
    TimBinned_ex, popRate_ex, hist_ex = bin_array(np.around(np.concatenate(spikes_excitatory) - begin, 1), bin,
                                                  time_array, nb_ex, dt)
    TimBinned_in, popRate_in, hist_in = bin_array(np.around(np.concatenate(spikes_inhibitory) - begin, 1), bin,
                                                  time_array, nb_in, dt)
    TimBinned_ex += begin
    TimBinned_in += begin

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
    if fig is None:
        fig = plt.figure(figsize=(20, 20))
        # plt.suptitle(title)
    if grid is None:
        grid = gridspec.GridSpec(3, 2, figure=fig)
    else:
        grid = gridspec.GridSpecFromSubplotSpec(30, 2, subplot_spec=grid[nb_grid, 0])

    ax_hist_ex = fig.add_subplot(grid[0:7, 0])
    grid_ECOG = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=grid[10:, 0], hspace=0.01, wspace=0.15)
    ECOG_1 = fig.add_subplot(grid_ECOG[0, 0])
    ECOG_2 = fig.add_subplot(grid_ECOG[0, 1])
    ax_rate = fig.add_subplot(grid[:, 1])

    # histogram
    ax_hist_ex.plot(time_array + begin, hist_ex, 'r', linewidth=0.1, alpha=0.2)
    if nb_grid == 2:
        ax_hist_ex.set_ylabel('IFR (Hz)    ', labelpad=-2, fontdict=font_labels, )
    else:
        ax_hist_ex.set_ylabel('IFR (Hz)', labelpad=2, fontdict=font_labels, )
    # ax_hist_ex.set_xlabel('time in ms')
    ax_hist_ex.plot(TimBinned_ex, popRate_ex, 'r', label='excitatory population')
    ax_hist_ex.set_xlim(xmin=begin - 100, xmax=end + 100)
    ax_hist_ex.tick_params(axis='both', labelsize=font_ticks_size)

    # # print compare rate
    # index = [26, 31, 96, 78, 83, 44]
    # max_rate = np.nanmax(state_variable[:, 1, index]) * 1e3
    # for j, i in enumerate(index):
    #     if j % 3 == 0:
    #         ax_rate_compare.plot(state_times, state_variable[:, 0, i] * 1e3 + j * max_rate, 'k', linewidth=1.0)
    #     else:
    #         ax_rate_compare.plot(state_times, state_variable[:, 0, i] * 1e3 + j * max_rate, 'r', linewidth=1.0)
    #         ax_rate_compare.plot(state_times, state_variable[:, 1, i] * 1e3 + j * max_rate, 'b', linewidth=1.0)
    # scalebar = AnchoredSizeBar(ax_rate_compare.transData,
    #                            size=0.1, label='30Hz', loc='center right',
    #                            pad=0.0,
    #                            borderpad=0.0,
    #                            color='red',
    #                            frameon=False,
    #                            size_vertical=20)
    # ax_rate_compare.add_artist(scalebar)
    # # ax_rate_compare.set_xlabel('time in ms')
    # ax_rate_compare.set_ylabel('Region Id')
    # position = [i * max_rate + max_rate / 2 for i in range(len(index))]
    # position_label = [i for i in index]
    # ax_rate_compare.set_yticklabels(position_label)
    # ax_rate_compare.set_yticks(position)
    # ax_rate_compare.set_xlim(xmax=end)

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
    ax_rate.set_ylabel('Region Id', labelpad=-6, fontdict=font_labels)
    ax_rate.set_ylim(ymin=-max_rate, ymax=max_rate * (nb_regions + 1.0))
    ax_rate.set_xlim(xmin=begin - 100, xmax=end + 100)
    ax_rate.tick_params(axis='both', labelsize=font_ticks_size)

    # ECOG
    for index, ax in enumerate([ECOG_1, ECOG_2]):
        max_ecog = np.nanmax(ECOG[:, :])
        custom_cycler = (cycler(color=plt.cm.jet(np.linspace(0, 1, 7))))
        ax.set_prop_cycle(custom_cycler)
        for i in range(8):
            ax.plot(ECOG_time, ECOG[:, i + index * ECOG.shape[1] // 2] + i * max_ecog, linewidth=0.1)
        ax.tick_params(axis='both', which='both', left='off', bottom='off', labelbottom='off', length=0)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.setp(ax.get_yticklabels(), visible=False)
        ax.set_ylabel('set of electrodes ' + str(index), labelpad=1, fontdict=font_labels)
    ECOG_1.set_xlabel('Time (ms)', labelpad=1, fontdict=font_labels)
    plt.setp(ECOG_1.get_xticklabels(), visible=True)
    ECOG_1.tick_params(axis='x', which='both', left='on',
                       bottom='on', labelbottom='on', length=1.0, labelsize=font_ticks_size)
    ECOG_2.set_xlabel('Time (ms)', labelpad=1, fontdict=font_labels)
    plt.setp(ECOG_2.get_xticklabels(), visible=True)
    ECOG_2.tick_params(axis='x', which='both', left='on',
                       bottom='on', labelbottom='on', length=1.0, labelsize=font_ticks_size)


def print_figure_macro(parameters, begin, end):
    """
    create the figure for the paper
    :param parameters: parameter for the getting data
    :param begin: start of plot
    :param end: end of the plot
    :return:
    """
    fig = plt.figure(figsize=(6.8, 8.56))
    plt.subplots_adjust(top=0.99, bottom=0.05, left=0.06, right=0.99, hspace=0.13, wspace=0.13)
    # plt.suptitle(param['title'])
    grid = gridspec.GridSpec(len(parameters), 1, figure=fig)
    for index, param in enumerate(parameters):
        data = get_data_all(param['result_path'] + '/nest/')
        rates = get_rate(param['result_path'] + '/tvb/')
        rates[1] = np.load(param['result_path'] + '/tvb/ECOG.npy', allow_pickle=True)
        print_figure_macro_one(
            param, begin, end, data['pop_1_ex'], data['pop_1_in'], rates,
            grid=grid, nb_grid=index, fig=fig
        )
        print(index)

    # add letters
    fig.add_artist(Text(0.01, 0.99, "a", fontproperties={'size': 7}))
    fig.add_artist(Text(0.01, 0.66, "b", fontproperties={'size': 7}))
    fig.add_artist(Text(0.01, 0.34, "c", fontproperties={'size': 7}))

    # plt.show()
    plt.savefig("figure/TVB_figure.pdf", dpi=300)
    plt.savefig("figure/TVB_figure.png", dpi=150)


if __name__ == '__main__':
    param_default = {}
    param_default['param_nest'] = {}
    param_default['param_nest']["sim_resolution"] = 0.1
    param_default['param_tvb_model'] = {}
    param_default['param_tvb_model']['T'] = 20.0
    param_default['param_nest_topology'] = {}
    param_default['param_nest_topology']["percentage_inhibitory"] = 0.2
    param_default['param_nest_topology']["nb_neuron_by_region"] = 10000
    param_default['param_nest_topology']["nb_region"] = 104

    params = []
    param_asynchronous = copy.copy(param_default)
    param_asynchronous['result_path'] = '../local_cluster/case_asynchronous/'
    param_asynchronous['title'] = " Asynchronous network "
    params.append(param_asynchronous)
    param_up_down = copy.copy(param_default)
    param_up_down['result_path'] = '../local_cluster/case_up_down/'
    param_up_down['title'] = " Synchronise network "
    params.append(param_up_down)
    param_regular_burst = copy.copy(param_default)
    param_regular_burst['result_path'] = '../local_cluster/case_regular_burst/'
    param_regular_burst['title'] = " Regular Bursting network "
    params.append(param_regular_burst)

    # paper figure
    print_figure_macro(params, 42500.0, 53500.0)
