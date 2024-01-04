#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import h5py
import matplotlib.pyplot as plt
import MEAutility
import numpy as np

from print_electrode import create_cross_section
from print_connectome import display_connectome, print_connectome_graph
from plot_electrode_morphologie import plot_electrode_neurons
from image_3d.mouse_sphere import print_mouse

if __name__ == "__main__":
    import os

    path = os.path.dirname(os.path.realpath(__file__))
    color_Nest = [255 / 255, 104 / 255, 65 / 255]
    color_TVB = [71 / 255, 164 / 255, 226 / 255]
    image_FMRI = h5py.File(path + '/parameter/data_mouse/StructuralMRI.h5', 'r', libver='latest')['array_data'][39, :, :].T
    param = {'param_nest_connection': {"path_weight": path + '/parameter/data_mouse/weights.npy',
                                       "path_distance": path + '/parameter/data_mouse/distance.npy',
                                       "velocity": 3.0},
             'param_co_simulation': {"id_region_nest": [26, 78]},
             'param_nest_topology': {"nb_region": 104},
             'param_tvb_connection': {'path_region_labels': path + '/parameter/data_mouse/region_labels.txt',
                                      'path_centers': path + '/parameter/data_mouse/centres.txt'
                                      },
             "param_tvb_monitor": {
                 "SEEG": False,
             }
             }
    ## plot cross section with electode
    create_cross_section(param, image=image_FMRI,
                         color_Nest=color_Nest, color_TVB=color_TVB,
                         alpha_image=1.0, size_edges=0.5, threshold=0.05, node=False, figsize=(2.22, 1.01),
                         electrodes=[[0, 1, 0]],
                         electrodes_position=[[76, 62]], reverse=False
                         )
    plt.subplots_adjust(top=1.0, bottom=0., left=0.0, right=1.0, hspace=0.0, wspace=0.0)
    plt.savefig(path + '/../data/figure/fig_2_cross_section.pdf', dpi=300)

    ## plot electrode
    path_LFP = path + "/../data/local_cluster/case_regular_burst/LFPY/v1/pop_1_/populations/"
    morphology = {
        'ex': path + '/parameter/morphologies/pyramidal_cell_14VbTest.hoc',
        'in': path + "/parameter/morphologies/basket_cell17S.hoc"}
    electrodeParams = {
        # ELECTRODE SHAPE
        'probe': MEAutility.return_mea('Neuronexus-32'),
    }

    # print electrode alone
    fig = plt.figure(figsize=(0.28, 2.22))
    ax = plt.gca()
    MEAutility.plot_probe(electrodeParams['probe'], ax=ax)
    plt.axis('off')
    plt.subplots_adjust(top=1.0, bottom=0., left=0.0, right=1.0, hspace=0.0, wspace=0.0)
    plt.savefig(path+'/../data/figure/fig_2_electrode.pdf', dpi=300)

    # print electrode in the middle of neurons
    fig = plt.figure(figsize=(2.22, 1.01))
    ax = plt.gca()
    plot_electrode_neurons(ax, X=['ex', 'in'], markers=['^', 'o'], colors=['r', 'b'],
                           isometricangle=np.pi / 12,
                           populations_path=path_LFP,
                           morphology=morphology,
                           radius=2000.0,
                           layerBoundaries=[[500, 100], [100, -400]],
                           electrodeParams=electrodeParams,
                           fraction=0.1)
    plt.subplots_adjust(top=1.0, bottom=0., left=0.0, right=1.0, hspace=0.0, wspace=0.0)
    plt.savefig(path + '/../data/figure/fig_2_electrode_neurons.pdf', dpi=300)

    ## mouse brian with electrode
    print_mouse(path+'/parameter/data_mouse/', 'mouse_brain.stl', 'centres.txt',
                [71 / 255, 164 / 255, 226 / 255, 1.0], [255 / 255, 104 / 255, 65 / 255, 0.5],
                Nest_node=[26, 78],
                electrode='electrode_hypocampus.txt', electrode_ECOG='sensor_hypocampus.txt',
                transparency=0.2,  # or 1.0
                save_path=path + '../data/figure/fig_2_mouse_elect.pdf',
                figsize=(1200, 1200)
                )

    print_connectome_graph(param, color_Nest=color_Nest, color_TVB=color_TVB,
                           size_node_TVB=5.0, size_node_Nest=10.0, linewidths=0.1,
                           alpha_image=1.0, size_edges=0.1, threshold=0.05, figsize=(2.22, 1.57))
    plt.subplots_adjust(top=1.0, bottom=0., left=0.0, right=1.0, hspace=0.0, wspace=0.0)
    plt.savefig(path + '/../data/figure/fig_2_graph.pdf', dpi=300)

    display_connectome(param, color_Nest=color_Nest, font_ticks_size=7, figsize=(2.2, 1.01), title_print=False,
                       wspace=0.7, hspace=0.0, top=0.995, right=0.89, bottom=0.05, left=0.09, linewidth=0.1)
    plt.savefig(path + '/../data/figure/fig_2_connectome.pdf', dpi=300)
