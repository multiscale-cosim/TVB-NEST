import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import networkx as nx

def display_connectome(param, image=None, alpha_image=0.4, threshold=1.0, size_edges=1.0, color_Nest='royalblue', color_TVB='tomato',
                       size_node_TVB=50.0, size_node_Nest=100.0, alpha_node=1.0):
    """
    print three figure and some text about the connectome for the simulation
    :param param: parameter for the simulation
    # parameter for display the graph (only available if the centers of regions is available)
    # parameter for the background image
    :param image: the image to ad in background of the graph
    :param alpha_image: the transparency of the image
    # parameter for edge of the graph
    :param threshold: the threshold for the plotting edge of the connectome
    :param size_edges: size of the line of the edges
    # parameter for nodes of the graph
    :param color_Nest: the color of node simulate with Nest
    :param color_TVB: the color of node simulate with TVB
    :param size_node_TVB: the size of the node simulate with TVB
    :param size_node_Nest: the size of the node simulate with Nest
    :param alpha_node: the transparency of the node
    :return:
    """
    weights = np.load(param['param_nest_connection']["path_weight"])
    weights[np.where(weights == 0.0)] = np.NAN
    delays = np.load(param['param_nest_connection']["path_distance"]) / param['param_nest_connection']["velocity"]
    ids = param['param_co_simulation']["id_region_nest"]
    nb_regions = param['param_nest_topology']["nb_region"]

    # Plot weights and delays
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 4))
    # plot weight
    axis_1 = axs[0]
    cs = axis_1.imshow(np.log10(weights), cmap='jet', aspect='equal', interpolation='none')
    axis_1.set_title('Structural connectivity matrix', fontsize=15)
    axcb = fig.colorbar(cs, fraction=0.046, pad=0.04, ax=axis_1)
    axcb.set_label('Log10(weights)', fontsize=15)
    # Create a Rectangle patch
    for i in ids:
        rect = Rectangle((0, i), nb_regions, 1, linewidth=1, edgecolor=color_Nest, facecolor='none')
        axis_1.add_patch(rect)
        rect = Rectangle((i, 0), 1, nb_regions, linewidth=1, edgecolor=color_Nest, facecolor='none')
        axis_1.add_patch(rect)

        # plot delay
    axis_2 = axs[1]
    cs = axis_2.imshow(delays)
    fig.colorbar(cs, fraction=0.046, pad=0.04, ax=axis_2)
    axis_2.set_title('Delay connectivity matrix', fontsize=15)
    # Create a Rectangle patch
    for i in ids:
        rect = Rectangle((0, i), nb_regions, 1, linewidth=1, edgecolor=color_Nest, facecolor='none')
        axis_2.add_patch(rect)
        rect = Rectangle((i, 0), 1, nb_regions, linewidth=1, edgecolor=color_Nest, facecolor='none')
        axis_2.add_patch(rect)

    #     # add the label of regions
    #     plt.xticks(range(len(labels)),labels,size=4.5, rotation='vertical')
    #     plt.yticks(range(len(labels)),labels,size=4.5)
    #     plt.subplots_adjust(left=0.20, bottom=0, right=0.9, top=1, wspace=0, hspace=0)
    title = "Nest will simulate the " + str(len(ids)) + " regions"
    fig.suptitle(title)
    plt.subplots_adjust(wspace=0.3, top=0.8)

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

    # plot 2d connectome
    if 'path_centers' in param['param_tvb_connection'].keys():
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
        fig, ax = plt.subplots(figsize=(9.5, 6))
        G = nx.from_numpy_matrix(weights_threshold)
        nx.draw(G, width=size_edges, pos=Nposition, edge_color='#909089', ax=ax, node_color=color_nodes,
                node_size=size_nodes,
                node_shape='o', alpha=alpha_node)
        # display an image if one is give (change perhaps the format)
        if image is not None:
            image = np.load(image)
            plt.imshow(image, cmap='gray', vmin=image.min(), vmax=image.max(), alpha=alpha_image)
            plt.xlim(xmax=image.shape[1], xmin=0)
            plt.ylim(ymax=image.shape[0], ymin=0)
        else:
            plt.xlim(xmax=np.max(Nposition[:, 0]) + 0.1, xmin=np.min(Nposition[:, 0]) - 0.1)
            plt.ylim(ymax=np.max(Nposition[:, 1]) + 0.1, ymin=np.min(Nposition[:, 1]) - 0.1)
