#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import os
import numpy as np
import h5py
from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt
import LFPy
import MEAutility
from .example_plotting import remove_axis_junk


def plot_electrode_neurons(ax, X, isometricangle, markers, colors,
                           populations_path, morphology, radius, layerBoundaries,
                           electrodeParams, fraction=1.):
    """
    plot electrode and neurons
    function inspired from example plotting
    :param ax: matplotlib.axes.AxesSubplot
    :param X: str : name of population
    :param isometricangle:  float : pseudo-3d view angle
    :param markers: array of str : the symbols for the neurons
    :param colors: array of color : the colors
    :param populations_path:  str : path to the file of the population
    :param morphology: neuron morphology
    :param radius: radius of the layer
    :param layerBoundaries: position of the layer
    :param electrodeParams: electrode parameters
    :param fraction: fraction of neurons
    :return:
    """
    remove_axis_junk(ax, ['right', 'bottom', 'left', 'top'])

    # DRAW OUTLINE OF POPULATIONS
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    r = radius

    # plot layers
    theta0 = np.linspace(0, np.pi, 20)
    theta1 = np.linspace(np.pi, 2 * np.pi, 20)
    zpos = np.r_[np.array(layerBoundaries)[:, 0],
                 np.array(layerBoundaries)[-1, 1]]
    for i, zval in enumerate(zpos):
        if i == 0:
            ax.plot(r * np.cos(theta0),
                    r * np.sin(theta0) * np.sin(isometricangle) + zval,
                    color='k', zorder=-r, clip_on=False)
            ax.plot(r * np.cos(theta1),
                    r * np.sin(theta1) * np.sin(isometricangle) + zval,
                    color='k', zorder=r, clip_on=False)
        else:
            ax.plot(r * np.cos(theta0),
                    r * np.sin(theta0) * np.sin(isometricangle) + zval,
                    color='gray', zorder=-r, clip_on=False)
            ax.plot(r * np.cos(theta1),
                    r * np.sin(theta1) * np.sin(isometricangle) + zval,
                    color='k', zorder=r, clip_on=False)

    # plot neurons
    for (pop, marker, color) in zip(X, markers, colors):
        # get the somapos
        fname = os.path.join(populations_path,
                             '%s_population_somapos.gdf' % pop)

        somapos = np.loadtxt(fname).reshape((-1, 3))
        n = somapos.shape[0]

        rotations = [{} for x in range(n)]
        fname = os.path.join(populations_path,
                             '%s_population_rotations.h5' % pop)
        f = h5py.File(fname, 'r')

        for key, value in list(f.items()):
            for i, rot in enumerate(value[()]):
                rotations[i].update({key: rot})

        # plot some units
        for j in range(int(n * fraction)):
            cell = LFPy.Cell(morphology=morphology[pop],
                             nsegs_method='lambda_f',
                             lambda_f=100,
                             extracellular=False
                             )
            cell.set_pos(somapos[j, 0], somapos[j, 1], somapos[j, 2])
            cell.set_rotation(**rotations[j])

            # set up a polycollection
            zips = []
            for x, z in cell.get_idx_polygons():
                zips.append(list(zip(x, z - somapos[j, 1] * np.sin(isometricangle)
                                     )))

            polycol = PolyCollection(zips,
                                     edgecolors='gray',
                                     facecolors=color,
                                     linewidths=(0.01),
                                     zorder=somapos[j, 1],
                                     clip_on=False,
                                     rasterized=False)

            ax.add_collection(polycol)

    # plot electrode
    probe = electrodeParams['probe']
    MEAutility.plot_probe(probe, ax=ax, xlim=ax.get_xlim(), ylim=ax.get_ylim(), top=600, alpha_prb=0.5)


if __name__ == '__main__':
    path = "/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/local/case_regular_burst/LFPY/small_init_test_image/pop_1_/populations"
    morphology = {
        'ex': os.path.dirname(os.path.realpath(__file__)) + '/../../parameter/morphologies/pyramidal_cell_14VbTest.hoc',
        'in': os.path.dirname(os.path.realpath(__file__)) + "/../../parameter/morphologies/basket_cell17S.hoc"}
    electrodeParams = {
        # ELECTRODE SHAPE
        'probe': MEAutility.return_mea('Neuronexus-32'),
    }

    # print electrode alone
    MEAutility.plot_probe(electrodeParams['probe'])
    plt.axis('off')

    # print electrode in the middle of neurons
    fig = plt.figure()
    ax = plt.gca()
    plot_electrode_neurons(ax, X=['ex', 'in'], markers=['^', 'o'], colors=['r', 'b'],
                           isometricangle=np.pi / 12,
                           populations_path=path,
                           morphology=morphology,
                           radius=2000.0,
                           layerBoundaries=[[500, 100], [100, -400]],
                           electrodeParams=electrodeParams,
                           fraction=0.1)
    plt.show()
