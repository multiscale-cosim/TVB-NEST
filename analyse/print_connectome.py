#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import networkx as nx


def display_connectome(param, color_Nest='royalblue', figsize=(9.5, 4), title_print=True, font_ticks_size=15,
                       wspace=0.3, hspace=0.2, top=0.8, right=None, bottom=None, left=None, linewidth=1.0):
    """
    plot matrix of the connectome with some text for identify NEST region
    :param param: parameter for the simulation
    :param color_Nest: the color of node simulate with Nest
    :param figsize: size of the figure
    :param title_print : print the title of the graph
    :param font_ticks_size: size of the ticks and labels
    :param wspace: maptlotlib adjust parameter
    :param hspace: maptlotlib adjust parameter
    :param top: maptlotlib adjust parameter
    :param right: maptlotlib adjust parameter
    :param bottom: maptlotlib adjust parameter
    :param left: maptlotlib adjust parameter
    :param linewidth: line of the rectangular of the node simulated with NEST
    :return:
    """

    weights = np.load(param['param_nest_connection']["path_weight"])
    weights[np.where(weights == 0.0)] = np.NAN
    tract_length = np.load(param['param_nest_connection']["path_distance"])
    ids = param['param_co_simulation']["id_region_nest"]
    nb_regions = param['param_nest_topology']["nb_region"]

    # Plot weights and delays
    fig, axs = plt.subplots(1, 2, figsize=figsize)
    # plot weight
    axis_1 = axs[0]
    cs = axis_1.imshow(np.log10(weights), cmap='jet', aspect='equal', interpolation='none')
    if title_print:
        axis_1.set_title('Structural connectivity matrix', fontsize=font_ticks_size)
    axcb = fig.colorbar(cs, fraction=0.046, pad=0.1, ax=axis_1)
    axcb.set_label('Log10(weights)', fontsize=font_ticks_size, labelpad=1)
    axcb.ax.tick_params(axis='both', labelsize=font_ticks_size, pad=1, bottom=False, top=False, left=False, right=False)
    axcb.ax.locator_params(axis='y', nbins=4)
    axis_1.tick_params(axis='both', labelsize=font_ticks_size, pad=1, bottom=False, top=False, left=False, right=False)
    axis_1.locator_params(axis='both', nbins=4)
    axis_1.set_ylim(ymax=nb_regions, ymin=0)
    axis_1.set_xlim(xmax=nb_regions, xmin=0)
    # Create a Rectangle patch
    for i in ids:
        rect = Rectangle((0, i), nb_regions, 1, linewidth=linewidth, edgecolor=color_Nest, facecolor='none')
        axis_1.add_patch(rect)
        rect = Rectangle((i, 0), 1, nb_regions, linewidth=linewidth, edgecolor=color_Nest, facecolor='none')
        axis_1.add_patch(rect)

    # plot delay
    axis_2 = axs[1]
    cs = axis_2.imshow(tract_length)
    axcb = fig.colorbar(cs, fraction=0.046, pad=0.1, ax=axis_2)
    if title_print:
        axis_2.set_title('Track length', fontsize=font_ticks_size)
    axcb.set_label('mm', fontsize=font_ticks_size, labelpad=1)
    axcb.ax.tick_params(axis='both', labelsize=font_ticks_size, pad=1, bottom=False, top=False, left=False, right=False)
    axcb.ax.locator_params(axis='y', nbins=4)
    axis_2.tick_params(axis='both', labelsize=font_ticks_size, pad=1, bottom=False, top=False, left=False, right=False)
    axis_2.locator_params(axis='both', nbins=4)
    axis_2.set_ylim(ymax=nb_regions, ymin=0)
    axis_2.set_xlim(xmax=nb_regions, xmin=0)

    # Create a Rectangle patch
    for i in ids:
        rect = Rectangle((0, i), nb_regions, 1, linewidth=linewidth, edgecolor=color_Nest, facecolor='none')
        axis_2.add_patch(rect)
        rect = Rectangle((i, 0), 1, nb_regions, linewidth=linewidth, edgecolor=color_Nest, facecolor='none')
        axis_2.add_patch(rect)

    #     # add the label of regions
    #     plt.xticks(range(len(labels)),labels,size=4.5, rotation='vertical')
    #     plt.yticks(range(len(labels)),labels,size=4.5)
    #     plt.subplots_adjust(left=0.20, bottom=0, right=0.9, top=1, wspace=0, hspace=0)
    if title_print:
        title = "Nest will simulate the " + str(len(ids)) + " regions"
        fig.suptitle(title)
    plt.subplots_adjust(wspace=wspace, hspace=hspace, top=top, right=right, bottom=bottom, left=left)

    # describe the region selected for the simulation with Nest
    if 'path_region_labels' in param['param_tvb_connection'].keys():
        labels = np.genfromtxt(param['param_tvb_connection']['path_region_labels'], dtype=str)
        message = " "
        for i in labels[ids]:
            if i != labels[ids[-1]]:
                message += i + ", "
            else:
                message += i
        print('\x1b[4;03;30m', "Nest simulate the following regions :", '\x1b[0m', message)


def print_connectome_graph(param, threshold, image=None, alpha_image=0.4,
                           size_edges=1.0, color_Nest='royalblue', color_TVB='tomato',
                           size_node_TVB=50.0, size_node_Nest=100.0, alpha_node=1.0,
                           figsize=(20, 20), linewidths=1.0):
    """
    plot the connectome in form of graph ( plot only the highest connection of the connectome)
    :param param: parameter for the simulation
    # parameter for display the graph (only available if the centers of regions is available)
    # parameter for the background image
    :param threshold: the threshold for the plotting edge of the connectome
    :param image: the image to ad in background of the graph
    :param alpha_image: the transparency of the image
    # parameter for edge of the graph
    :param size_edges: size of the line of the edges
    # parameter for nodes of the graph
    :param color_Nest: the color of node simulate with Nest
    :param color_TVB: the color of node simulate with TVB
    :param size_node_TVB: the size of the node simulate with TVB
    :param size_node_Nest: the size of the node simulate with Nest
    :param alpha_node: the transparency of the node
    :param figsize: size of the figure
    :param linewidths: line of the circle around the node
    :return:
    """
    weights = np.load(param['param_nest_connection']["path_weight"])
    weights[np.where(weights == 0.0)] = np.NAN
    ids = param['param_co_simulation']["id_region_nest"]
    nb_regions = param['param_nest_topology']["nb_region"]

    # get position of the node
    centres = np.loadtxt(param['param_tvb_connection']['path_centers'])
    Nposition = np.swapaxes(centres[:2, :], 0, 1)
    # select edges to show
    weights_threshold = weights
    weights_threshold[np.where(weights_threshold < threshold)] = 0.0
    # select the color for the nodes
    color_nodes = [color_TVB for i in range(nb_regions)]
    for id in ids:
        color_nodes[id] = color_Nest
    # select the size of the nodes
    size_nodes = np.array([size_node_TVB for i in range(nb_regions)])
    size_nodes[ids] = size_node_Nest

    # create the graph and print it
    fig, ax = plt.subplots(figsize=figsize)
    G = nx.from_numpy_matrix(weights_threshold)
    nx.draw(G, width=size_edges, pos=Nposition, edge_color='#909089', ax=ax, node_color=color_nodes,
            node_size=size_nodes,
            node_shape='o', alpha=alpha_node, linewidths=linewidths)
    # display an image if one is give (change perhaps the format)
    if image is not None:
        plt.imshow(image, cmap='gray', vmin=image.min(), vmax=image.max(), alpha=alpha_image)
        plt.xlim(xmax=image.shape[1], xmin=0)
        plt.ylim(ymax=image.shape[0], ymin=0)
    else:
        plt.xlim(xmax=np.max(Nposition[:, 0]) + size_node_TVB * 1.1e-1,
                 xmin=np.min(Nposition[:, 0]) - size_node_TVB * 1.1e-1)
        plt.ylim(ymax=np.max(Nposition[:, 1]) + size_node_TVB * 1.1e-1,
                 ymin=np.min(Nposition[:, 1]) - size_node_TVB * 1.1e-1)
        plt.subplots_adjust(top=1.0, bottom=0.0, right=1.0, left=0.0)
    ax.invert_yaxis()


if __name__ == '__main__':
    import h5py

    param = {'param_nest_connection': {"path_weight": '../../example/parameter/data_mouse/weights.npy',
                                       "path_distance": '../../example/parameter/data_mouse/distance.npy',
                                       "velocity": 3.0},
             'param_co_simulation': {"id_region_nest": [26, 78]},
             'param_nest_topology': {"nb_region": 104},
             'param_tvb_connection': {'path_region_labels': '../../example/parameter/data_mouse/region_labels.txt',
                                      'path_centers': '../../example/parameter/data_mouse/centres.txt'
                                      }
             }
    color_Nest = [255 / 255, 104 / 255, 65 / 255]
    color_TVB = [71 / 255, 164 / 255, 226 / 255]
    image_FMRI = h5py.File('../../example/parameter/data_mouse/StructuralMRI.h5',
                           'r', libver='latest')['array_data'][:,:, 40].T
    # display_connectome(param, image=image_FMRI,
    #                    color_Nest=color_Nest, color_TVB=color_TVB,
    #                    size_edges=0.5,
    #                    threshold=0.05)
    # plt.show()
    display_connectome(param,
                       color_Nest=color_Nest, color_TVB=color_TVB,
                       alpha_image=1.0, size_edges=0.5, threshold=0.05, figsize=(10, 20))
    # plot 2d connectome
    if 'path_centers' in param['param_tvb_connection'].keys():
        print_connectome_graph(param, color_Nest=color_Nest, color_TVB=color_TVB,
                               alpha_image=1.0, size_edges=0.5, threshold=0.05, figsize=(10, 20))

    plt.show()
