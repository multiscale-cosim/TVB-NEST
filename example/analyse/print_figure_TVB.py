#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from nest_elephant_tvb.translation.translation_function.rate_spike import slidding_window
import matplotlib.ticker as tkr
from cycler import cycler
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar

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


def print_tvb_figure(param, begin, end, spikes_ex, spikes_in, TVB_data):
    """
    print TVB figure
    :param param: parameter of the figure
    :param begin: start of measure
    :param end: en of measure
    :param spikes_ex: spike of excitaotry neurons
    :param spikes_in: spikes of inhibitory neurons
    :param TVB_data: rate of regions
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
    fig = plt.figure(figsize=(20, 20))
    grid = gridspec.GridSpec(3, 2, figure=fig)
    ax_hist_ex = fig.add_subplot(grid[0, 0])
    grid_ECOG = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=grid[1:, 0], hspace=0.01, wspace=0.15)
    ECOG_1 = fig.add_subplot(grid_ECOG[0, 0])
    ECOG_2 = fig.add_subplot(grid_ECOG[0, 1])
    ax_rate = fig.add_subplot(grid[:, 1])

    # histogram
    ax_hist_ex.plot(time_array + begin, hist_ex, 'r', linewidth=0.1, alpha=0.2)
    ax_hist_ex.set_ylabel('IFR (Hz)')
    # ax_hist_ex.set_xlabel('time in ms')
    ax_hist_ex.set_ylabel('IFR (Hz)')
    ax_hist_ex.plot(TimBinned_ex, popRate_ex, 'r', label='excitatory population')

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
            ax_rate.plot(state_times, state_variable[:, 0, i] * 1e3 + i * max_rate, 'r', linewidth=1.0)
            ax_rate.plot(state_times, state_variable[:, 1, i] * 1e3 + i * max_rate, 'b', linewidth=1.0)
    position = [i * max_rate + max_rate / 2 for i in
                np.array(np.around(np.linspace(0, nb_regions - 1, 5)), dtype=np.int)]
    position_label = [i for i in np.array(np.around(np.linspace(0, nb_regions - 1, 5)), dtype=np.int)]
    ax_rate.set_yticklabels(position_label)
    ax_rate.set_yticks(position)
    ax_rate.set_xlabel('Time (ms)')
    ax_rate.set_ylabel('Region Id')

    # ECOG
    for index, ax in enumerate([ECOG_1, ECOG_2]):
        max_ecog = np.nanmax(ECOG[:, :])
        custom_cycler = (cycler(color=plt.cm.jet(np.linspace(0, 1, 7))))
        ax.set_prop_cycle(custom_cycler)
        for i in range(8):
            ax.plot(ECOG_time, ECOG[:, i + index * ECOG.shape[1]//2] + i * max_ecog, linewidth=0.1)
        ax.tick_params(axis='both', which='both', left='off', bottom='off', labelbottom='off', length=0)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.setp(ax.get_yticklabels(), visible=False)
        ax.set_ylabel('set of electrodes ' + str(index))
    ECOG_1.set_xlabel('Time (ms)')
    plt.setp(ECOG_1.get_xticklabels(), visible=True)
    ECOG_1.tick_params(axis='x', which='both', left='on', bottom='on', labelbottom='on', length=1.0)
    ECOG_2.set_xlabel('Time (ms)')
    plt.setp(ECOG_2.get_xticklabels(), visible=True)
    ECOG_2.tick_params(axis='x', which='both', left='on', bottom='on', labelbottom='on', length=1.0)

    plt.subplots_adjust(wspace=0.1,left=0.04,right=0.98,top=0.98,bottom=0.06)
    plt.show()


if __name__ == '__main__':
    from example.analyse.get_data import get_data_all, get_rate

    param = {}
    param['param_nest'] = {}
    param['param_nest']["sim_resolution"] = 0.1
    param['param_tvb_model'] = {}
    param['param_tvb_model']['T'] = 20.0
    param['param_nest_topology'] = {}
    param['param_nest_topology']["percentage_inhibitory"] = 0.2
    param['param_nest_topology']["nb_neuron_by_region"] = 10000
    param['param_nest_topology']["nb_region"] = 104
    id_proxy = [26, 78]
    data = get_data_all('../local_cluster//case_regular_burst/nest/'); title = " Regular Bursting network "; rates = get_rate('../local_cluster//case_regular_burst/tvb/'); ecog_max= 16.0; rates[1] = np.load('../local_cluster//case_regular_burst/tvb/ECOG.npy',allow_pickle=True)
    # data = get_data_all('../local_cluster//case_asynchronous/nest/'); title = " Asynchronous network "; rates = get_rate('../local_cluster//case_asynchronous/tvb/'); ecog_max= 2.0; rates[1] = np.load('../local_cluster//case_asynchronous/tvb/ECOG.npy',allow_pickle=True)
    # data = get_data_all('../local_cluster//case_up_down/nest/'); title = " Synchronise network "; rates = get_rate('../local_cluster//case_up_down/tvb/'); ecog_max= 2.0 ; rates[1] = np.load('../local_cluster//case_up_down/tvb/ECOG.npy',allow_pickle=True)
    # data = get_data_all('../local//case_asynchronous/nest/'); title = " Asynchronous network "; rates = get_rate('../local//case_asynchronous/tvb/')
    # data = get_data_all('../local//case_regular_burst/nest/'); title = " Regular Bursting network "; rates = get_rate('../local//case_regular_burst/tvb/')
    # data = get_data_all('../local//case_up_down/nest/'); title = " Synchronise network "; rates = get_rate('../local//case_up_down/tvb/')
    # data = get_data_all('../piz_daint/sarus/v1/case_up_down_1/nest/'); title = " Regular Bursting network ";rates = get_rate('../piz_daint/sarus/v1/case_up_down_1/tvb/')
    # data = get_data_all('../piz_daint/sarus/v1/case_regular_burst/nest/'); title = " Regular Bursting network ";rates = get_rate('../piz_daint/sarus/v1/case_regular_burst/tvb/')
    # data = get_data_all('../local//case_up_down/nest/'); title = " Regular Bursting network "; rates = get_rate('../local//case_regular_burst/tvb/')
    # test for the plot
    # print_tvb_figure(param, 000.0, 100000.0, data['pop_1_ex'], data['pop_1_in'], rates)
    # # paper figure
    print_tvb_figure(param, 42500.0, 53500.0,data['pop_1_ex'],data['pop_1_in'],rates,max_ecog=ecog_max)

    # print compare rate
    nb_regions = 104
    # result_raw= rates
    # result_raw = get_rate('../local//case_regular_burst/tvb/')
    # result_raw = get_rate('../local//case_up_down/tvb/')
    # result_raw = get_rate('../piz_daint/sarus/v1/case_up_down_1/tvb/')
    state_times = result_raw[0][0]
    state_variable = np.concatenate(result_raw[0][1]).reshape((result_raw[0][1].shape[0], 7, 104))
    index = [26, 31, 96, 78, 83, 44]
    max_rate = np.nanmax(state_variable[:, 1, index]) * 1e3
    plt.figure()
    ax_rate_compare = plt.gca()
    for j, i in enumerate(index):
        if j % 3 == 0:
            ax_rate_compare.plot(state_times, state_variable[:, 0, i] * 1e3 + j * max_rate, 'k', linewidth=1.0)
        else:
            ax_rate_compare.plot(state_times, state_variable[:, 0, i] * 1e3 + j * max_rate, 'r', linewidth=1.0)
            ax_rate_compare.plot(state_times, state_variable[:, 1, i] * 1e3 + j * max_rate, 'b', linewidth=1.0)
    scalebar = AnchoredSizeBar(ax_rate_compare.transData,
                               size=0.1, label='30Hz', loc='center right',
                               pad=0.0,
                               borderpad=0.0,
                               color='red',
                               frameon=False,
                               size_vertical=20)
    ax_rate_compare.add_artist(scalebar)
    # ax_rate_compare.set_xlabel('time in ms')
    ax_rate_compare.set_ylabel('Region Id')
    position = [i * max_rate + max_rate / 2 for i in range(len(index))]
    position_label = [i for i in index]
    ax_rate_compare.set_yticklabels(position_label)
    ax_rate_compare.set_yticks(position)
    # ax_rate_compare.set_xlim(xmax=10000.0)

    # print rate
    plt.figure()
    ax_rate = plt.gca()
    max_rate = np.nanmax(state_variable[:, 1, :]) * 1e3
    print(max_rate)
    for i in range(nb_regions):
        if i in [26, 78]:
            ax_rate.plot(state_times, state_variable[:, 0, i] * 1e3 + i * max_rate, 'k', linewidth=1.0)
        else:
            ax_rate.plot(state_times, state_variable[:, 0, i] * 1e3 + i * max_rate, 'r', linewidth=1.0)
            ax_rate.plot(state_times, state_variable[:, 1, i] * 1e3 + i * max_rate, 'b', linewidth=1.0)
    position = [i * max_rate + max_rate / 2 for i in
                np.array(np.around(np.linspace(0, nb_regions - 1, 5)), dtype=np.int)]
    position_label = [i for i in np.array(np.around(np.linspace(0, nb_regions - 1, 5)), dtype=np.int)]
    ax_rate.set_yticklabels(position_label)
    ax_rate.set_yticks(position)
    ax_rate.set_xlabel('Time (ms)')
    ax_rate.set_ylabel('Region Id')


    # ECOG
    end = 10000.0
    begin = 000.0
    ECOG_time = result_raw[1][0]
    ECOG = np.array([i for i in result_raw[1][1]])[:, 0, :, 0]
    mask = np.where(np.logical_and(ECOG_time < end, ECOG_time > begin))
    ECOG_time = ECOG_time[mask]
    ECOG = ECOG[mask]
    plt.figure()
    ECOG_1 = plt.subplot(4, 1, 1)
    rate_26 = plt.subplot(4, 1, 2)
    ECOG_2 = plt.subplot(4, 1, 3)
    rate_78 = plt.subplot(4, 1, 4)
    # ECOG
    for index, ax in enumerate([ECOG_1, ECOG_2]):
        max_ecog = np.nanmax(ECOG[:, :])
        custom_cycler = (cycler(color=plt.cm.jet(np.linspace(0, 1, 7))))
        ax.set_prop_cycle(custom_cycler)
        for i in range(8):
            ax.plot(ECOG_time, ECOG[:, i + index * int(ECOG.shape[1]/2)] + i * max_ecog, linewidth=1.0)
        ax.tick_params(axis='both', which='both', left='off', bottom='off', labelbottom='off', length=0)
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.setp(ax.get_yticklabels(), visible=False)
        ax.set_ylabel('electrode ' + str(index))
    ECOG_1.set_xlabel('Time (ms)')
    plt.setp(ECOG_1.get_xticklabels(), visible=True)
    ECOG_1.tick_params(axis='x', which='both', left='on', bottom='on', labelbottom='on', length=1.0)
    ECOG_2.set_xlabel('Time (ms)')
    plt.setp(ECOG_2.get_xticklabels(), visible=True)
    ECOG_2.tick_params(axis='x', which='both', left='on', bottom='on', labelbottom='on', length=1.0)

    mask_rate = np.where(np.logical_and(state_times < end, state_times > begin))[0]
    rate_26.plot(state_times[mask_rate], state_variable[mask_rate, 0, 26] * 1e3, 'k', linewidth=1.0)
    rate_78.plot(state_times[mask_rate], state_variable[mask_rate, 0, 78] * 1e3, 'k', linewidth=1.0)
    plt.show()
