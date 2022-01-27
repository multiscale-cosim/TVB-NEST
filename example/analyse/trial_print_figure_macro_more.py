import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from cycler import cycler
from example.analyse.get_data import get_rate


def print_compare_rate(result_raw, nb_regions, index):
    # figure compare rate
    state_times = result_raw[0][0]
    state_variable = np.concatenate(result_raw[0][1]).reshape((result_raw[0][1].shape[0], 7, 104))
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


def print_Ecog(result_raw):
    state_times = result_raw[0][0]
    state_variable = np.concatenate(result_raw[0][1]).reshape((result_raw[0][1].shape[0], 7, 104))
    # print ECOG
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
            ax.plot(ECOG_time, ECOG[:, i + index * int(ECOG.shape[1] / 2)] + i * max_ecog, linewidth=1.0)
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


if __name__ == '__main__':
    nb_regions = 104
    index = [26, 31, 96, 78, 83, 44]
    rate = get_rate('../local//case_regular_burst/tvb/')
    # result_raw = get_rate('../local//case_up_down/tvb/')
    # result_raw = get_rate('../piz_daint/sarus/v1/case_up_down_1/tvb/')
    print_compare_rate(rate, nb_regions, index)
    print_Ecog(rate)
    plt.show()
