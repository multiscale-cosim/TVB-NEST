#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
import matplotlib.pyplot as plt
from nest_elephant_tvb.transformation.transformation_function.rate_spike import rates_to_spikes

np.set_printoptions(linewidth=300, precision=1, threshold=100000)


def print_rate_to_spike(folder_simulation, begin, end, selected_region=4, nb_regions=104,
                        nb_synapse=1, percentage_shared=0.1, nb_spike_generator=100,
                        size_neurons=10.0, font_ticks_size=30, figure_size=(20, 20),
                        linewidth=1.0, pad=2):
    """
    print spike and rate for transformation rate to spike
    :param folder_simulation: folder of the simulation
    :param begin: start of the measure
    :param end: end of the measure
    :param selected_region: number of region
    :param nb_regions: total number of number
    :param nb_synapse: number of synapse
    :param percentage_shared: percentage for sharing people
    :param nb_spike_generator: number of neurons
    :param size_neurons: size of the print of neurons
    :param figure_size: figure size
    :param font_ticks_size: font size of the ticks and label
    :param linewidth: width of the line of the plot
    :param pad: pad for the labels
    :return:
    """
    from example.analyse.get_data import get_rate
    from quantities import ms, Hz
    result_raw = get_rate(folder_simulation + '/tvb/')[0]  # result of the Raw monitor

    # separate the different variable
    times = result_raw[0]
    state_variable = np.concatenate(result_raw[1]).reshape((result_raw[1].shape[0], 7, nb_regions))[:, 0,
                     :selected_region] * 1e3  # shape : time, state variable, region
    max_FE = np.max(state_variable)

    # print figure of rate
    fig_1 = plt.figure(figsize=figure_size)
    ax = plt.gca()
    for i in range(selected_region):
        plt.plot(times - begin, state_variable[:, i] + max_FE * i, linewidth=linewidth)
    # plt.ylabel('firing rate (Hz)')
    # plt.xlabel('Time (ms)')
    # plt.title('firing rate of excitatory population')
    plt.ylim(ymin=-1.0, ymax=max_FE * selected_region)
    plt.xlim(xmin=0, xmax=end - begin)
    position = [i * max_FE + max_FE / 5 for i in np.arange(0, selected_region, 1)]
    position_label = [i for i in np.arange(0, selected_region, 1)]
    ax.set_yticklabels(position_label)
    ax.set_yticks(position)
    ax.get_yaxis().set_ticks_position('right')
    ax.tick_params(axis='both', labelsize=font_ticks_size, pad=pad)

    # print of spikes
    fig_2 = plt.figure(figsize=figure_size)
    ax = plt.gca()
    for id_region in range(selected_region):
        rate = state_variable[:, id_region]
        # Multiple Interaction Process Model
        rate *= nb_synapse / percentage_shared  # rate of poisson generator ( due property of poisson process)
        rate += 1e-12  # avoid rate equals to zeros
        spike_shared = np.round(rates_to_spikes(rate * Hz, begin * ms, end * ms, variation=True)[0], 1)
        select = np.random.binomial(n=1, p=percentage_shared, size=(nb_spike_generator, spike_shared.shape[0]))
        for index, i in enumerate(np.repeat([spike_shared], nb_spike_generator, axis=0) * select):
            plt.scatter(i[np.where(i != 0)] - begin,
                        id_region * nb_spike_generator + np.ones(np.where(i != 0)[0].shape) * index, s=size_neurons,
                        c='r')
    plt.xlim(xmin=0, xmax=end - begin)
    position = [i for i in np.array(np.around(np.linspace(0, nb_spike_generator * selected_region, 4)), dtype=int)]
    position_label = [i for i in
                      np.array(np.around(np.linspace(0, nb_spike_generator * selected_region, 4)), dtype=int)]
    ax.set_yticklabels(position_label)
    ax.set_yticks(position)
    plt.ylim(ymin=-1.0, ymax=nb_spike_generator * selected_region)
    ax.tick_params(axis='both', labelsize=font_ticks_size, pad=pad)

    return fig_1, fig_2


def print_spike_to_rate(folder_simulation, nb_neurons, begin_1, begin_2, time_end, size_neurons=10.0, dt=0.1,
                        width=200, font_ticks_size=30, figure_size=(20, 20),
                        linewidth=1.0, pad=2):
    """
    print spike and rate for transformation spike to rate
    :param folder_simulation: folder of the simulation
    :param nb_neurons: number of neurons
    :param begin_1: first start of measure
    :param begin_2: second start of measure
    :param time_end: the time of measure
    :param size_neurons: the size of neurons
    :param dt: the time step
    :param width: the width of period
    :param figure_size: figure size
    :param font_ticks_size: font size of the ticks and label
    :param linewidth: width of the line of the plot
    :param pad: pad for the labels
    :return:
    """
    from example.analyse.get_data import get_data_all
    from nest_elephant_tvb.transformation.transformation_function.rate_spike import slidding_window
    # get data
    data_1 = get_data_all(folder_simulation + '/nest/')['pop_1_ex']
    data_2 = get_data_all(folder_simulation + '/nest/')['pop_2_ex']
    spikes_1 = []
    spikes_2 = []
    spikes_3 = []
    spikes_4 = []
    for index in range(nb_neurons):
        spike = data_1[1][index]
        spikes_1.append(spike[np.where(np.logical_and(spike > begin_1, spike < begin_1 + time_end))] - begin_1)
        spikes_2.append(spike[np.where(np.logical_and(spike > begin_2, spike < begin_2 + time_end))] - begin_2)
        spike = data_2[1][index]
        spikes_3.append(spike[np.where(np.logical_and(spike > begin_1, spike < begin_1 + time_end))] - begin_1)
        spikes_4.append(spike[np.where(np.logical_and(spike > begin_2, spike < begin_2 + time_end))] - begin_2)
    spikes = spikes_1 + spikes_2 + spikes_3 + spikes_4

    # print spikes
    fig_1 = plt.figure(figsize=figure_size)
    ax = plt.gca()
    for i in range(len(spikes)):
        plt.scatter(spikes[i], np.repeat(i, spikes[i].shape[0]), c='r', s=size_neurons)
    # plt.xlabel('Time (ms)')
    # plt.ylabel('Neuron index')
    position = [i for i in np.array(np.around(np.linspace(0, nb_neurons * 4, 4)), dtype=int)]
    position_label = [i for i in np.array(np.around(np.linspace(0, nb_neurons * 4, 4)), dtype=int)]
    ax.set_yticklabels(position_label)
    ax.set_yticks(position)
    plt.ylim(ymin=-size_neurons, ymax=nb_neurons * 4 + size_neurons)
    plt.xlim(xmin=0, xmax=time_end)
    ax.tick_params(axis='both', labelsize=font_ticks_size, pad=pad)

    # get data of rate
    hist = [np.zeros(int(time_end / dt)) for i in range(4)]
    for i in range(nb_neurons):
        hist[0][np.array(np.around(spikes_1[i]), dtype=int)] += 1
        hist[1][np.array(np.around(spikes_2[i]), dtype=int)] += 1
        hist[2][np.array(np.around(spikes_3[i]), dtype=int)] += 1
        hist[3][np.array(np.around(spikes_4[i]), dtype=int)] += 1

    for i in range(4):
        hist[i] = slidding_window(hist[i], width=width) * 1e3

    # print rate
    max_FE = np.max(hist)
    fig_2 = plt.figure(figsize=figure_size)
    ax = plt.gca()
    for i in range(4):
        plt.plot(hist[i] + max_FE * i, linewidth=linewidth)
    # plt.ylabel('firing rate (Hz)')
    # plt.xlabel('Time (ms)')
    # plt.title('firing rate of excitatory population')
    plt.ylim(ymin=-1.0, ymax=max_FE * 4)
    plt.xlim(xmin=0, xmax=time_end)
    position = [i * max_FE + max_FE / 5 for i in np.arange(0, 4, 1)]
    position_label = [i for i in np.arange(0, 4, 1)]
    ax.set_yticklabels(position_label)
    ax.set_yticks(position)
    ax.get_yaxis().set_ticks_position('right')
    ax.tick_params(axis='both', labelsize=font_ticks_size, pad=pad)

    return fig_1, fig_2


if __name__ == '__main__':
    # test function
    # print_rate_to_spike('../local_cluster/case_regular_burst/', 1000.0, 20000.0)
    # print_spike_to_rate('../local_cluster/case_regular_burst/', 100, 100.0, 200.0, 1000.0)
    # plt.show()
    # plot for first figure
    fig_1, fig_2 = print_rate_to_spike('../local_cluster/case_up_down/', 10000.0, 20000.0,
                                       figure_size=(0.9, 0.63), font_ticks_size=5, size_neurons=0.001,
                                       linewidth=0.1, pad=0)
    plt.figure(fig_1.number)
    plt.subplots_adjust(top=0.99, bottom=0.18, left=0.02, right=0.88)
    plt.savefig("figure/fig_1_rate_to_spike_rate.pdf", dpi=300)
    plt.figure(fig_2.number)
    plt.subplots_adjust(top=0.94, bottom=0.18, left=0.21, right=0.88)
    plt.savefig("figure/fig_1_rate_to_spike_spike.pdf", dpi=300)

    fig_3, fig_4 = print_spike_to_rate('../local_cluster/case_up_down/', 100, 10000.0, 20000.0, 10000.0,
                                       figure_size=(0.9, 0.63), font_ticks_size=5, size_neurons=0.001,
                                       linewidth=0.1, pad=0)
    plt.figure(fig_3.number)
    plt.subplots_adjust(top=0.94, bottom=0.18, left=0.21, right=0.88)
    plt.savefig("figure/fig_1_spike_to_rate_spike.pdf", dpi=300)
    plt.figure(fig_4.number)
    plt.subplots_adjust(top=0.99, bottom=0.18, left=0.02, right=0.88)
    plt.savefig("figure/fig_1_spike_to_rate_rate.pdf", dpi=300)
