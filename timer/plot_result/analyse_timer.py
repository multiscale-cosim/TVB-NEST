#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import numpy as np
from timer.plot_result.get_time_data import get_dictionnary
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def print_tree_data(data_time, id_TR_N_to_T, id_TR_T_to_N):
    """
    Function for plotting the time of all the modules
    :param data_time: tree with time
    :param id_TR_N_to_T: the ids of Transformer Nest to TVB
    :param id_TR_T_to_N: the ids of Transformer TVB to Nest
    :return:
    """
    # get times for Nest
    values = []
    labels = []
    parents = []
    values_nest, labels_nest, parents_nest = data_time.get('Nest').to_array_for_print()
    values.append(values_nest)
    labels.append(labels_nest)
    parents.append(parents_nest)

    # get times for TVB
    values_tvb, labels_tvb, parents_tvb = data_time.get('TVB').to_array_for_print()
    values.append(values_tvb)
    labels.append(labels_tvb)
    parents.append(parents_tvb)

    # get times for transformer Nest to TVB
    for index_tr, i in enumerate(id_TR_N_to_T):
        for name in [': Producer Nest data ', ': Transformer function ', ': Consumer TVB data ']:
            TR = data_time.get('TVB_NEST_' + str(index_tr) + name)
            values_TR, labels_TR, parents_TR = TR.to_array_for_print()
            values.append(values_TR)
            labels.append(labels_TR)
            parents.append(parents_TR)

    # get times for transformer TVB to Nest
    for index_tr, i in enumerate(id_TR_T_to_N):
        for name in [': Consumer Nest data ', ': Transformer function ', ': Producer TVB data ']:
            TR = data_time.get('NEST_TVB_' + str(index_tr) + name)
            values_TR, labels_TR, parents_TR = TR.to_array_for_print()
            values.append(values_TR)
            labels.append(labels_TR)
            parents.append(parents_TR)

    # concatenate every values and if each labels are unique
    for labels_sim in labels:
        if np.unique(labels_sim).shape[0] != len(labels_sim):
            count = np.unique(labels_sim, return_counts=True)[1]
            print(np.array(np.unique(labels_sim))[np.where(count != 1)])
            raise Exception('error label not unique in : ' + str(labels_sim))

    marker_size = 25.0
    # create the tree to plot
    fig = make_subplots(
        rows=5, cols=3,
        column_widths=np.repeat([1 / 3], 3).tolist(),
        specs=np.repeat([np.repeat([{'type': 'treemap', 'rowspan': 1}], 3)], 5, axis=0).tolist(),
        vertical_spacing=0.0001,
        horizontal_spacing=0.0001,
    )
    # Nest
    trace = go.Treemap(
        labels=labels[0],
        values=values[0],
        parents=parents[0],
        branchvalues='total',
        textinfo="label+value+percent entry",
        # marker_colorscale = 'greens',
        maxdepth=4,
    )
    trace.marker.pad.update({'t': marker_size})
    fig.add_trace(trace, col=1, row=1)
    # TVB
    trace = go.Treemap(
        labels=labels[1],
        values=values[1],
        parents=parents[1],
        branchvalues='total',
        textinfo="label+value+percent entry",
        maxdepth=4
    )
    trace.marker.pad.update({'t': marker_size})
    fig.add_trace(trace, col=3, row=1)
    # TRANSFORMATION
    for i in range(4):
        for j in range(3):
            trace = go.Treemap(
                labels=labels[2 + (i * 3) + j],
                values=values[2 + (i * 3) + j],
                parents=parents[2 + (i * 3) + j],
                branchvalues='total',
                textinfo="label+value+percent entry",
            )
            trace.marker.pad.update({'t': marker_size})
            fig.add_trace(trace, col=1 + j, row=2 + i)

    # plot the tree
    # fig.update_layout(height=1100, width=1800, title_text="Simulation 10000 neurons MPI=8 time_syn=3.5",
    #                   uniformtext_minsize=20, font={'size': 40})
    # fig.update_layout(uniformtext=dict(minsize=7, mode='hide'))
    fig.update_layout(treemapcolorway = ['#17becf', '#ff7f0e','#17becf'],height=2000, width=1000)
    fig.show()
    fig.write_image("timer_reference.svg", scale=1)


if __name__ == '__main__':
    # dict_time, index = get_dictionnary('./test_file/test_MPI/_g_1.0_mean_I_ext_0.0/',True)
    # dict_time, index = get_dictionnary('./test_file/test_MPI/ln_g_1.0_mean_I_ext_0.0/',True)
    # dict_time, index = get_dictionnary('./test_file/test_thread/_g_1.0_mean_I_ext_0.0/',False)
    dict_time, index = get_dictionnary('./test_file/paper_time_synch/2.0/0/_g_10.0_mean_I_ext_0.0/', False)
    print_tree_data(dict_time, index[0], index[1])
    # print_data_time(dict_time, index[0], index[1]) doesn't work
    print('end')
