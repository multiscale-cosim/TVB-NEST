#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
import networkx as nx
from tvb.datatypes.sensors import SensorsInternal
import os


def create_cross_section(param, image=None, alpha_image=0.4, node=False, threshold=1.0, size_edges=1.0,
                         color_Nest='royalblue', color_TVB='tomato',
                         size_node_TVB=50.0, size_node_Nest=100.0, alpha_node=1.0, electrodes=None, figsize=(20, 20),
                         reverse=True, electrodes_position=None):
    """
    :param param: parameter for the simulation
    # parameter for the background image
    :param image: the image to ad in background of the graph
    :param alpha_image: the transparency of the image
    :param node : if there presence or not of the graph
    # parameter for edge of the graph
    :param threshold: the threshold for the plotting edge of the connectome
    :param size_edges: size of the line of the edges
    # parameter for nodes of the graph
    :param color_Nest: the color of node simulate with Nest
    :param color_TVB: the color of node simulate with TVB
    :param size_node_TVB: the size of the node simulate with TVB
    :param size_node_Nest: the size of the node simulate with Nest
    :param alpha_node: the transparency of the node
    # parameter for showing the electrode
    :param electrodes : array of [number of contact point, color in RGB]
    or
    :param electrodes: position
    :param electrodes_position: position of ECOG electrode ( hard code of the angles need to increase the flexibility)
    :return:
    """
    weights = np.load(param['param_nest_connection']["path_weight"])
    weights[np.where(weights == 0.0)] = np.NAN
    ids = param['param_co_simulation']["id_region_nest"]
    nb_regions = param['param_nest_topology']["nb_region"]

    # plot 2d connectome
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
    fig = plt.figure(figsize=figsize)
    ax = plt.gca()
    if node:
        G = nx.from_numpy_matrix(weights_threshold)
        nx.draw(G, width=size_edges, pos=Nposition, edge_color='#909089', ax=ax, node_color=color_nodes,
                node_size=size_nodes,
                node_shape='o', alpha=alpha_node)
    if electrodes is not None:
        if param['param_tvb_monitor']['SEEG']:
            path = param['param_tvb_monitor']['parameter_SEEG']['path']
            sensor = SensorsInternal().from_file(os.path.abspath(path))
            positions = sensor.locations
            count = 0
            for electrode in electrodes:
                for i in range(electrode[0]):
                    plt.plot(positions[count][0], positions[count][1], '*',
                             color=[electrode[1], electrode[2], electrode[3]])
                    count += 1
        else:
            for i in range(len(electrodes_position)):
                ax.add_patch(Rectangle((electrodes_position[i][0] - 0.5, electrodes_position[i][1] - 0.5), 1,
                                       np.max(Nposition[:, 1]) - electrodes_position[i][1], alpha=0.5,
                                       color=[electrodes[i][0], electrodes[i][1], electrodes[i][2]]))
                plt.plot(electrodes_position[i][0], electrodes_position[i][1], 'o',
                         color=[191 / 255, 191 / 255, 0 / 255])

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
    if reverse:
        ax.invert_yaxis()
    plt.axis('off')


if __name__ == '__main__':
    import h5py
    import os

    path = os.path.dirname(os.path.realpath(__file__))

    color_Nest = [255 / 255, 104 / 255, 65 / 255]
    color_TVB = [71 / 255, 164 / 255, 226 / 255]
    # version one of implemented electrode : old code
    param = {'param_nest_connection': {"path_weight": path + '/parameter/data_mouse/weights.npy'},
             'param_co_simulation': {"id_region_nest": [26, 78]},
             'param_nest_topology': {"nb_region": 104},
             'param_tvb_connection': {'path_region_labels': path + '/parameter/data_mouse/region_labels.txt',
                                      'path_centers': path + '/parameter/data_mouse/centres.txt'
                                      },
             "param_tvb_monitor": {
                 "SEEG": True,
                 "parameter_SEEG": {"path": path + "/parameter/data_mouse/sensor_hypocampus_V1.txt"}}
             }
    image_FMRI = h5py.File(path + '/parameter/data_mouse/StructuralMRI.h5', 'r', libver='latest')['array_data'][:, :,
                 40].T
    create_cross_section(param, image=image_FMRI,
                         color_Nest=color_Nest, color_TVB=color_TVB,
                         alpha_image=1.0, size_edges=0.5, threshold=0.05, node=True)
    create_cross_section(param, image=image_FMRI,
                         alpha_image=1.0, electrodes=[[14, 0, 1, 0], [28, 191 / 255, 191 / 255, 0 / 255]])

    # version 2
    image_FMRI = h5py.File(path+'/parameter/data_mouse/StructuralMRI.h5', 'r', libver='latest')['array_data'][39, :, :].T
    param = {'param_nest_connection': {"path_weight": path+'/parameter/data_mouse/weights.npy'},
             'param_co_simulation': {"id_region_nest": [26, 78]},
             'param_nest_topology': {"nb_region": 104},
             'param_tvb_connection': {'path_region_labels': path+'/parameter/data_mouse/region_labels.txt',
                                      'path_centers': path+'/parameter/data_mouse/centres.txt'
                                      },
             "param_tvb_monitor": {
                 "SEEG": False,
             }
             }
    # plot only connectome in spatial dimension
    create_cross_section(param,
                         color_Nest=color_Nest, color_TVB=color_TVB,
                         alpha_image=1.0, size_edges=0.5, threshold=0.05, node=True, figsize=(10, 20),
                         )
    # create a cross section based on FMRI for implemented electrode
    create_cross_section(param, image=image_FMRI,
                         color_Nest=color_Nest, color_TVB=color_TVB,
                         alpha_image=1.0, size_edges=0.5, threshold=0.05, node=False, figsize=(10, 20),
                         electrodes=[[0, 1, 0]],
                         electrodes_position=[[76, 62]], reverse=False
                         )
    plt.show()
