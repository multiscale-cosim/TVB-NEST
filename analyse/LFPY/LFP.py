#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# modification of the example of Brunel from the folder HybridLFPy : https://github.com/INM-6/hybridLFPy/blob/master/examples/example_brunel.py

import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from hybridLFPy import PostProcess, Population, CachedNetwork, setup_file_dest
import MEAutility
import lfpykit
from parameters import ParameterSet
import h5py
from mpi4py import MPI
import neuron
import json
import sys
import copy
from analyse.LFPY.select_spikes import select_spikes

################# Initialization of MPI stuff ##################################
if not hasattr(neuron.h, 'ExpSynI'):
    neuron.load_mechanisms(os.path.dirname(__file__))


def param_set_up(path, save_folder, param, parameters):
    """
    set the parameter for the simulation
    :param path: path of simulation
    :param save_folder: folder to save the result
    :param param: parameter for LFP
    :param parameters: parameter of the co-simulation
    :return: Parameters in good format
    """
    ################################################################################
    ## PARAMETERS
    ################################################################################
    # set up file destinations differentiating between certain output
    PS = ParameterSet(dict(
        # Main folder of simulation output
        savefolder=save_folder,

        # make a local copy of main files used in simulations
        sim_scripts_path=os.path.join(save_folder, 'sim_scripts'),

        # destination of single-cell output during simulation
        cells_path=os.path.join(save_folder, 'cells'),

        # destination of cell- and population-specific signals, i.e., compund LFPs,
        # CSDs etc.
        populations_path=os.path.join(save_folder, 'populations'),

        # location of spike output from the network model
        spike_output_path=os.path.join(path + '/nest/'),

        # destination of figure file output generated during model execution
        figures_path=os.path.join(save_folder, 'figures')
    ))

    # population (and cell type) specific parameters
    PS.update(dict(
        # no cell type specificity within each E-I population
        # hence X == x and Y == X
        X=['ex', 'in'],

        # population-specific LFPy.Cell parameters
        cellParams={
            # excitory cells
            'ex': dict(
                morphology=param['morphologie_ex'],
                v_init=parameters['param_nest_topology']['param_neuron_excitatory']['E_L'],
                cm=parameters['param_nest_topology']['param_neuron_excitatory']['C_m'],
                Ra=param['Ra'],
                passive=param['passive'],
                passive_parameters=dict(
                    g_pas=parameters['param_nest_topology']['param_neuron_excitatory']['g_L'] * 1e-3,
                    e_pas=parameters['param_nest_topology']['param_neuron_excitatory']['E_L']),
                nsegs_method=param['nsegs_method'],
                lambda_f=param['lambda_f'],
                dt=parameters['param_nest']["sim_resolution"],
                tstart=parameters['begin'],
                tstop=parameters['end'],
                verbose=param['verbose'],
            ),
            # inhibitory cells
            'in': dict(
                morphology=param['morphologie_in'],
                v_init=parameters['param_nest_topology']['param_neuron_inhibitory']['E_L'],
                cm=parameters['param_nest_topology']['param_neuron_inhibitory']['C_m'],
                Ra=param['Ra'],
                passive=param['passive'],
                passive_parameters=dict(
                    g_pas=parameters['param_nest_topology']['param_neuron_inhibitory']['g_L'] * 1e-3,
                    e_pas=parameters['param_nest_topology']['param_neuron_inhibitory']['E_L']),
                nsegs_method=param['nsegs_method'],
                lambda_f=param['lambda_f'],
                dt=parameters['param_nest']["sim_resolution"],
                tstart=parameters['begin'],
                tstop=parameters['end'],
                verbose=param['verbose'],
            )},
        rand_rot_axis=param['rand_rot_axis'],
        simulationParams=dict(),  # kwargs passed to LFPy.Cell.simulate()
        populationParams=param['populationParams'],
        layerBoundaries=param['layerBoundaries'],
        electrodeParams=param['electrodeParams'],
        savelist=param['savelist'],
        # time resolution of saved signals
        dt_output=param['dt_output'],
    ))
    # for each population, define layer- and population-specific connectivity
    # parameters
    PS.update(dict(
        # number of connections from each presynaptic population onto each
        # layer per postsynaptic population, preserving overall indegree
        k_yXL={
            'ex': [[int(
             param['populationParams']['ex']['number'] * parameters['param_nest_connection']['p_connect'] * 0.5), 0],
             [int(param['populationParams']['ex']['number'] * parameters['param_nest_connection']['p_connect'] * 0.5),
              int(param['populationParams']['in']['number'] * parameters['param_nest_connection']['p_connect'])]],
            'in': [[0, 0],
                   [int(param['populationParams']['ex']['number'] * parameters['param_nest_connection']['p_connect']),
                    int(param['populationParams']['in']['number'] * parameters['param_nest_connection']['p_connect'])]],
        },

        # set up table of synapse weights from each possible presynaptic population
        J_yX={
            'ex': [parameters['param_nest_connection']['weight_local'],
                   parameters['param_nest_connection']['weight_local'] * parameters['param_nest_connection']['g']],
            'in': [parameters['param_nest_connection']['weight_local'],
                   parameters['param_nest_connection']['weight_local'] * parameters['param_nest_connection']['g']],
        },

        # set up synapse parameters as derived from the network
        synParams=param['synParams'],

        # set up table of synapse time constants from each presynaptic populations
        tau_yX={
            'ex': [parameters['param_nest_topology']['param_neuron_excitatory']['tau_syn_ex'],
                   parameters['param_nest_topology']['param_neuron_excitatory']['tau_syn_in']],
            'in': [parameters['param_nest_topology']['param_neuron_inhibitory']['tau_syn_ex'],
                   parameters['param_nest_topology']['param_neuron_inhibitory']['tau_syn_in']]
        },

        # set up delays, here using fixed delays of network
        synDelayLoc={
            'ex': [parameters['param_nest']["sim_resolution"], parameters['param_nest']["sim_resolution"]],
            'in': [parameters['param_nest']["sim_resolution"], parameters['param_nest']["sim_resolution"]],
        },
        # no distribution of delays
        synDelayScale={
            'ex': [None, None],
            'in': [None, None],
        },
    ))

    # putative mappting between population type and cell type specificity,
    # but here all presynaptic senders are also postsynaptic targets
    PS.update(dict(
        mapping_Yy=list(zip(PS.X, PS.X))
    ))

    return PS


def set_up_network_sim(path, label, simulation_time, GIDs_ex, GIDs_in, parameters):
    """
    set up the network for the LFP simulation
    :param path: path of the simulation
    :param label: label of the population
    :param GIDs_ex: ids of excitatory neurons
    :param GIDs_in: ids of inhibitory neurons
    :param parameters: parameters of the simulation
    :return: Network
    """
    # Create an object representation containing the spiking activity of the network
    # simulation output that uses sqlite3. Again, kwargs are derived from the brunel
    # network instance.
    networkSim = CachedNetwork(
        simtime=simulation_time,
        dt=parameters['param_nest']["sim_resolution"],
        spike_output_path=path,
        label=label,
        ext='dat',
        GIDs={'ex': [GIDs_ex[0], GIDs_ex[1]], 'in': [GIDs_in[0], GIDs_in[1]]},
        X=['ex', 'in'],
        cmap='rainbow_r',
    )
    return networkSim


def process(PS, parameters, networkSim):
    """
    SImulate the LFP
    :param PS: parameters
    :param parameters: parameters of the simulation
    :param networkSim: network
    :return:
    """
    ##### Set up LFPykit measurement probes for LFPs and CSDs
    probes = []
    probes.append(lfpykit.RecExtElectrode(cell=None, **PS.electrodeParams))

    ####### Set up populations #####################################################
    # iterate over each cell type, and create population simulation object
    for i, Y in enumerate(PS.X):
        # create population:
        pop = Population(
            cellParams=PS.cellParams[Y],
            rand_rot_axis=PS.rand_rot_axis[Y],
            simulationParams=PS.simulationParams,
            populationParams=PS.populationParams[Y],
            y=Y,
            layerBoundaries=PS.layerBoundaries,
            savelist=PS.savelist,
            savefolder=PS.savefolder,
            probes=probes,
            dt_output=PS.dt_output,
            POPULATIONSEED=parameters['param_nest']['master_seed'] + 40 + i,
            X=PS.X,
            networkSim=networkSim,
            k_yXL=PS.k_yXL[Y],
            synParams=PS.synParams[Y],
            synDelayLoc=PS.synDelayLoc[Y],
            synDelayScale=PS.synDelayScale[Y],
            J_yX=PS.J_yX[Y],
            tau_yX=PS.tau_yX[Y],
            save_in_file=True
        )

        # run population simulation and collect the data
        pop.run()
        # pop.collect_data()

        # object no longer needed
        del pop

    # reset seed, but output should be deterministic from now on
    np.random.seed(parameters['param_nest']['master_seed'] + 40 + len(PS.X))

    ####### Postprocess the simulation output ######################################
    # do some postprocessing on the collected data, i.e., superposition
    # of population LFPs, CSDs etc
    postproc = PostProcess(y=PS.X,
                           dt_output=PS.dt_output,
                           savefolder=PS.savefolder,
                           mapping_Yy=PS.mapping_Yy,
                           savelist=PS.savelist,
                           probes=probes,
                           cells_subfolder=os.path.split(PS.cells_path)[-1],
                           populations_subfolder=os.path.split(PS.populations_path)[-1],
                           figures_subfolder=os.path.split(PS.figures_path)[-1]
                           )

    # run through the procedure
    postproc.run()

    # create tar-archive with output for plotting, ssh-ing etc.
    postproc.create_tar_archive()


def plot_rasterplot(networkSim, T, PS):
    """
    Raster plot
    :param networkSim: Network simulation
    :param T: Time
    :param PS: Parameters
    :return:
    """
    # create network raster plot
    fig = networkSim.raster_plots(xlim=T, markersize=2.)
    fig.savefig(os.path.join(PS.figures_path, 'network.pdf'), dpi=300)
    plt.close(fig)


def plot_electrode(PS):
    """
    plot the electrode with neurons
    :param PS: parameters
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population
    fig, ax = plt.subplots(1, 1, figsize=(5, 8))
    plot_population(ax, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['ex', 'in'],
                    layers=['upper', 'lower'],
                    isometricangle=np.pi / 12, aspect='equal')
    fig.savefig(os.path.join(PS.figures_path, 'layers.pdf'), dpi=300)
    plt.close(fig)


def plot_soma(PS):
    """
    plot soma
    :param PS: parameters
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_soma_locations
    # plot cell locations
    fig, ax = plt.subplots(1, 1, figsize=(5, 8))
    plot_population(ax, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['ex', 'in'],
                    layers=['upper', 'lower'],
                    isometricangle=np.pi / 12, aspect='equal')
    plot_soma_locations(ax, X=['ex', 'in'],
                        populations_path=PS.populations_path,
                        markers=['^', 'o'], colors=['r', 'b'],
                        isometricangle=np.pi / 12, )
    fig.savefig(os.path.join(PS.figures_path, 'soma_locations.pdf'), dpi=300)
    plt.close(fig)


def plot_cell(PS):
    """
    plot the neurons
    :param PS:
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_morphologies
    # plot morphologies in their respective locations
    fig, ax = plt.subplots(1, 1, figsize=(5, 8))
    plot_population(ax, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['ex', 'in'],
                    layers=['upper', 'lower'],
                    aspect='equal')
    plot_morphologies(ax, X=['ex', 'in'], markers=['^', 'o'], colors=['r', 'b'],
                      isometricangle=np.pi / 12,
                      populations_path=PS.populations_path,
                      cellParams=PS.cellParams)
    fig.savefig(os.path.join(PS.figures_path, 'populations.pdf'), dpi=300)
    plt.close(fig)


def plot_cell_model(PS):
    """
    Plot the cell model
    :param PS:  parameters
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_individual_morphologies
    # plot morphologies in their respective locations
    fig, ax = plt.subplots(1, 1, figsize=(5, 8))
    plot_population(ax, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['ex', 'in'], markers=['^', 'o'], colors=['r', 'b'],
                    layers=['upper', 'lower'],
                    aspect='equal')
    plot_individual_morphologies(ax, X=['ex', 'in'], markers=['^', 'o'],
                                 colors=['r', 'b'],
                                 isometricangle=np.pi / 12,
                                 cellParams=PS.cellParams,
                                 populationParams=PS.populationParams)
    fig.savefig(os.path.join(PS.figures_path, 'cell_models.pdf'), dpi=300)
    plt.close(fig)


def plot_cell_and_indication(PS):
    """
    Plot neurons and some indication
    :param PS: parameters
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_morphologies
    # plot morphologies in their respective locations
    fig, ax = plt.subplots(1, 1, figsize=(5, 8))
    plot_population(ax, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['ex', 'in'],
                    layers=['upper', 'lower'],
                    aspect='equal')
    plot_morphologies(ax, X=['ex', 'in'], markers=['^', 'o'], colors=['r', 'b'],
                      isometricangle=np.pi / 12,
                      populations_path=PS.populations_path,
                      cellParams=PS.cellParams)

    # some additional plot annotations
    ax.text(-275, -300, 'ex', clip_on=False, va='center', zorder=500)
    ax.add_patch(plt.Rectangle((-290, -340), fc='r', ec='k', alpha=0.5,
                               width=80, height=80, clip_on=False, zorder=500))
    ax.arrow(-210, -300, 50, 50, head_width=20, head_length=20, width=10,
             fc='r', lw=1, ec='w', alpha=1, zorder=500)
    ax.arrow(-210, -300, 50, -50, head_width=20, head_length=20, width=10,
             fc='r', lw=1, ec='w', alpha=1, zorder=500)

    ax.text(-275, -400, 'in', clip_on=False, va='center', zorder=500)
    ax.add_patch(plt.Rectangle((-290, -440), fc='b', ec='k', alpha=0.5,
                               width=80, height=80, clip_on=False, zorder=500))
    ax.arrow(-210, -400, 50, 0, head_width=20, head_length=20, width=10, fc='b',
             lw=1, ec='w', alpha=1, zorder=500)

    fig.savefig(os.path.join(PS.figures_path, 'populations_vII.pdf'), dpi=300)
    plt.close(fig)


def plot_excitatory_cell(PS):
    """
    plot excitatory neurons and there activities
    :param PS: parameter
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_morphologies
    # plot ex morphologies in their respective locations
    fig, ax = plt.subplots(1, 1, figsize=(5, 8))
    plot_population(ax, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['ex'],
                    layers=['upper', 'lower'],
                    aspect='equal')
    plot_morphologies(ax, X=['ex'], markers=['^'], colors=['r'],
                      isometricangle=np.pi / 12,
                      populations_path=PS.populations_path,
                      cellParams=PS.cellParams)
    fig.savefig(os.path.join(PS.figures_path, 'EX_population.pdf'), dpi=300)
    plt.close(fig)


def plot_inhibitory_cell(PS):
    """
    plot inhibitory neurons and there activities
    :param PS: parameters
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_morphologies
    # plot IN morphologies in their respective locations
    fig, ax = plt.subplots(1, 1, figsize=(5, 8))
    plot_population(ax, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['in'],
                    layers=['upper', 'lower'],
                    isometricangle=np.pi / 12, aspect='equal')
    plot_morphologies(ax, X=['in'], markers=['o'], colors=['b'],
                      isometricangle=np.pi / 12,
                      populations_path=PS.populations_path,
                      cellParams=PS.cellParams)
    fig.savefig(os.path.join(PS.figures_path, 'IN_population.pdf'), dpi=300)
    plt.close(fig)


def plot_compute_signal(PS, T):
    """
    Plot the recorded signal
    :param PS: parameters
    :param T: times
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_morphologies, plot_signal_sum
    # plot compound LFP and CSD traces
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 8)

    ax0 = fig.add_subplot(gs[:, :2])
    ax1 = fig.add_subplot(gs[0, 4:])
    ax2 = fig.add_subplot(gs[1, 4:])
    ax1.set_title('CSD')
    ax2.set_title('LFP')

    plot_population(ax0, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['ex', 'in'],
                    layers=['upper', 'lower'],
                    isometricangle=np.pi / 12, aspect='equal')
    plot_morphologies(ax0, X=['ex', 'in'], markers=['^', 'o'],
                      colors=['r', 'b'],
                      isometricangle=np.pi / 12,
                      populations_path=PS.populations_path,
                      cellParams=PS.cellParams)

    plot_signal_sum(ax2, z=PS.electrodeParams['z'],
                    fname=os.path.join(PS.savefolder, 'RecExtElectrode_sum.h5'),
                    unit='mV', T=T)

    fig.savefig(os.path.join(PS.figures_path, 'compound_signals.pdf'), dpi=300)
    plt.close(fig)


def plot_excitatory_signal(PS, T):
    """
    plot excitatory neurons and the signals
    :param PS: parameter
    :param T: times
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_morphologies, plot_signal_sum
    # plot compound LFP and CSD traces
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 8)

    ax0 = fig.add_subplot(gs[:, :2])
    ax1 = fig.add_subplot(gs[0, 4:])
    ax2 = fig.add_subplot(gs[1, 4:])
    ax1.set_title('CSD')
    ax2.set_title('LFP')

    plot_population(ax0, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['ex'],
                    layers=['upper', 'lower'],
                    isometricangle=np.pi / 12, aspect='equal')
    plot_morphologies(ax0, X=['ex'], markers=['^'], colors=['r'],
                      isometricangle=np.pi / 12,
                      populations_path=PS.populations_path,
                      cellParams=PS.cellParams)

    plot_signal_sum(ax2, z=PS.electrodeParams['z'],
                    fname=os.path.join(PS.populations_path,
                                       'ex_population_RecExtElectrode.h5'),
                    unit='mV', T=T, color='r')
    fig.savefig(os.path.join(PS.figures_path, 'population_EX_signals.pdf'),
                dpi=300)
    plt.close(fig)


def plot_inhibitory_signal(PS, T):
    """
    plot inhibitory neurons and the signal
    :param PS: parameters
    :param T: times
    :return:
    """
    from analyse.LFPY.example_plotting import plot_population, plot_morphologies, plot_signal_sum
    # plot compound LFP and CSD traces
    fig = plt.figure()
    gs = gridspec.GridSpec(2, 8)

    ax0 = fig.add_subplot(gs[:, :2])
    ax1 = fig.add_subplot(gs[0, 4:])
    ax2 = fig.add_subplot(gs[1, 4:])
    ax1.set_title('CSD')
    ax2.set_title('LFP')

    plot_population(ax0, PS.populationParams, PS.electrodeParams,
                    PS.layerBoundaries,
                    X=['in'],
                    layers=['upper', 'lower'],
                    isometricangle=np.pi / 12, aspect='equal')
    plot_morphologies(ax0, X=['in'], markers=['o'], colors=['b'],
                      isometricangle=np.pi / 12,
                      populations_path=PS.populations_path,
                      cellParams=PS.cellParams)

    plot_signal_sum(ax2, z=PS.electrodeParams['z'],
                    fname=os.path.join(PS.populations_path,
                                       'in_population_RecExtElectrode.h5'),
                    unit='mV', T=T, color='b')
    fig.savefig(os.path.join(PS.figures_path, 'population_IN_signals.pdf'),
                dpi=300)
    plt.close(fig)


def plot_compute_all_signal(PS, T, networkSim, parameters):
    """
    Plot of signal
    :param PS: parameters
    :param T: time
    :param networkSim: network
    :param parameters: simulation parameters
    :return:
    """
    from analyse.LFPY.example_plotting import plot_signal_sum, plot_correlation
    # correlate global firing rate of network with CSD/LFP across channels
    # compute firing rates
    x, y = networkSim.get_xy((0, parameters['end']))
    bins = np.arange(0, parameters['end'] + 1)

    xx = np.r_[x['ex'], x['in']]

    fig = plt.figure()
    fig.subplots_adjust(hspace=0.5, wspace=0.5)
    gs = gridspec.GridSpec(4, 3)

    ax0 = fig.add_subplot(gs[0, :2])
    ax1 = fig.add_subplot(gs[1:, :2])
    ax2 = fig.add_subplot(gs[:, 2])

    ax0.hist(xx, bins=bins[500:], color='r')
    ax0.axis('tight')
    ax0.set_title('spike rate (s$^{-1}$)')

    plot_signal_sum(ax1, z=PS.electrodeParams['z'],
                    fname=os.path.join(PS.savefolder, 'RecExtElectrode_sum.h5'),
                    unit='mV', T=T)
    ax1.set_title('LFP')

    fname = os.path.join(PS.savefolder, 'RecExtElectrode_sum.h5')
    f = h5py.File(fname, 'r')
    data = f['data'][()]

    r, t = np.histogram(xx, bins)
    # plot_correlation(z_vec=PS.electrodeParams['z'], x0=r, x1=data[:, 1:],
    #                  ax=ax2, lag=50, title='rate-LFP xcorr')
    # plt.show()
    fig.savefig(os.path.join(PS.figures_path,
                             'compound_signal_correlations.pdf'), dpi=300)
    plt.close(fig)


def plot_all(parameters, networkSim, PS, morphology=False, position=False, signal=False):
    """
    plot of the graphics
    :param parameters: simulation parameters
    :param networkSim: network
    :param PS: parameter
    :param morphology: neuron morphology
    :param position: position of neurons
    :param signal: signal to plot
    :return:
    """
    T = (parameters['begin'], parameters['end'])
    if 'probe' in PS.electrodeParams.keys():
        probe = PS.electrodeParams['probe']
        PS.electrodeParams.update({
            'x': probe.positions[:, 0],
            'y': probe.positions[:, 1],
            'z': probe.positions[:, 2],
            'sigma': probe.sigma,
            'N': probe.normal,
            'r': probe.size,
        })
    if position:
        plot_electrode(PS)
        plot_soma(PS)
        pass
    if morphology:
        plot_cell(PS)
        plot_cell_model(PS)
        plot_cell_and_indication(PS)
        plot_excitatory_cell(PS)
        plot_inhibitory_cell(PS)
        pass
    if signal:
        plot_rasterplot(networkSim, T, PS)
        plot_compute_signal(PS, T)
        plot_compute_all_signal(PS, T, networkSim, parameters)
        plot_excitatory_signal(PS, T)
        plot_inhibitory_signal(PS, T)


def generate_LFP(path, label, begin, end, GIDs_ex, GIDs_in, properrun=True, name=''):
    """
    Generate LFP
    :param path: file of the simulation
    :param label: population label
    :param GIDs_ex: ids of excitatory neurons
    :param GIDs_in: ids of inhibitory neurons
    :param properrun: process LFP
    :param name: name of the LFP simulation
    :return:
    """
    COMM = MPI.COMM_WORLD
    SIZE = COMM.Get_size()
    RANK = COMM.Get_rank()
    print("rank :", RANK, " size : ", SIZE)
    with open(path + '/parameter.json') as f:
        parameters = json.load(f)
    parameters['begin'] = 0.0
    parameters['end'] = end - begin

    # # modification of parameter for testing
    # parameters['param_nest_topology']['nb_neuron_by_region'] = 20
    # parameters['param_nest_connection']['p_connect'] = 1.0
    # parameters['end'] = 1000.0

    # simulation time (always start at the beginning)
    # parameters['end'] = 10.0
    # parameters['end'] = 11000.0

    # number of neurons:
    # GIDs_ex[1] = int(parameters['param_nest_topology']['nb_neuron_by_region'] * (1 - parameters['param_nest_topology']['percentage_inhibitory']))
    # GIDs_in[1] = int(parameters['param_nest_topology']['nb_neuron_by_region'] * parameters['param_nest_topology']['percentage_inhibitory'])

    param = {
        'properrun': properrun,
        # if True, execute full model. If False, do only the plotting. Simulation results must exist.
        'morphologie_ex': os.path.dirname(
            os.path.realpath(__file__)) + '/../parameter/morphologies/pyramidal_cell_14VbTest.hoc',
        'morphologie_in': os.path.dirname(
            os.path.realpath(__file__)) + "/../parameter/morphologies/basket_cell17S.hoc",
        'Ra': 150.0,  # LFPy : Axial resistance (reduce it increase the LFP)
        'passive': True,  # LFPy : Passive mechanisms are initialized if True. Defaults to False
        'nsegs_method': 'lambda_f',
        # 'lambda100' or 'lambda_f' or 'fixed_length' or None nseg rule,
        # used by NEURON to determine number of compartments. Defaults to 'lambda100'
        'lambda_f': 100,
        'verbose': False,
        # assuming excitatory cells are pyramidal
        'rand_rot_axis': {'ex': ['z'], 'in': ['z']},
        # set up parameters corresponding to cylindrical model populations
        'populationParams': {'ex': {
            'number': GIDs_ex[1],
            'radius': 2000,
            'z_min': -50,
            'z_max': 50,
            'min_cell_interdist': 1.,
            'min_r': [[-1E199, -150, 700, 1E99], [0, 0, 1, 1]],
        },
            'in': {'number': GIDs_in[1],
                   'radius': 2000,
                   'z_min': -50,
                   'z_max': 50,
                   'min_cell_interdist': 1.,
                   'min_r': [[-1E199, -150, 700, 1E99], [0, 0, 1, 1]],
                   },
        },
        # set the boundaries between the "upper" and "lower" layer
        'layerBoundaries': [[700, 300], [300, -200]],
        # set the geometry of the virtual recording device
        'electrodeParams': {
            # extracellular conductivity:
            'sigma': 0.3,
            # ELECTRODE SHAPE
            'probe': MEAutility.return_mea('Neuronexus-32'),
            # 'seedvalue':None,
            # # dendrite line sources, soma as sphere source (Linden2014)
            'method': 'root_as_point',
        },
        # runtime, cell-specific attributes and output that will be stored
        'savelist': ['somav', 'somapos', 'x', 'y', 'z'],
        # time resolution of saved signals
        'dt_output': 0.1,
        'synParams': {'ex': {'section': ['soma', 'radTprox', 'radTmed', 'radTdist',
                                         'lm_thick1', 'lm_medium1', 'lm_thin1a', 'lm_thin1b',
                                         'lm_thick2', 'lm_medium2', 'lm_thin2a', 'lm_thin2b',
                                         'rad_thick1', 'rad_medium1', 'rad_thin1a', 'rad_thin1b',
                                         'rad_thick2', 'rad_medium2', 'rad_thin2a', 'rad_thin2b',
                                         'oriprox1', 'oridist1a', 'oridist1b', 'oriprox2', 'oridist2a', 'oridist2b'
                                         ], 'syntype': 'ExpSynI'},
                      'in': {'section': ['soma',
                                         'radProx1', 'radMed1', 'radDist1', 'lmM1', 'lmt1',
                                         'radProx2', 'radMed2', 'radDist2', 'lmM2', 'lmt2',
                                         'oriProx1', 'oriMed1', 'oriDist1',
                                         'oriProx2', 'oriMed2', 'oriDist2',
                                         ], 'syntype': 'ExpSynI'}
                      },

    }

    # set some seed values
    np.random.seed(parameters['param_nest']['master_seed'] + 42 + RANK)

    # parameters
    save_folder = path + '/LFPY/' + name + label + '/'
    PS = param_set_up(path, save_folder, param, parameters)

    if not os.path.exists(path + '/LFPY/' + name) and RANK == 0:
        os.makedirs(path + '/LFPY/' + name)
    if param['properrun']:
        # set up the file destination, removing old results by default
        setup_file_dest(PS, clearDestination=False)
    if RANK == 0:
        param_save = copy.deepcopy(param)
        if 'probe' in param_save['electrodeParams'].keys():
            param_save['electrodeParams']['probe'] = param_save['electrodeParams']['probe'].info['electrode_name']
        # if 'r' in param_save['electrodeParams'].keys() and hasattr(param_save['electrodeParams']['r'],'dtype'):
        #     param_save['electrodeParams']['r'] = list(param_save['electrodeParams']['r'])
        #     for index,i in enumerate(param_save['electrodeParams']['r']):
        #         param_save['electrodeParams']['r'][index] = int(i)
        # save parameter
        f = open(save_folder + '/parameter.json', "wt")
        json.dump(param_save, f)
        f.close()
        if not os.path.exists(path + '/LFPY/' + name + label + '/spikes/'):
            os.makedirs(path + '/LFPY/' + name + label + '/spikes/')
            select_spikes(begin, end, path + '/nest/', label + 'ex', path + '/LFPY/' + name + label + '/spikes/')
            select_spikes(begin, end, path + '/nest/', label + 'in', path + '/LFPY/' + name + label + '/spikes/')

    ################################################################################
    # MAIN simulation procedure                                                    #
    ################################################################################
    COMM.Barrier()
    print("rank", RANK, "network simulation  begin"); sys.stdout.flush()
    networkSim = set_up_network_sim(path + '/LFPY/' + name + label + '/spikes/', label, parameters['end'],
                                    GIDs_ex, GIDs_in, parameters)
    print("rank", RANK, "network simulation end"); sys.stdout.flush()
    if param['properrun']:
        print("rank", RANK, "process start"); sys.stdout.flush()
        process(PS, parameters, networkSim)
        print("rank", RANK, "process end"); sys.stdout.flush()
        COMM.Barrier()
        sys.stdout.flush()

    ################################################################################
    # Create set of plots from simulation output
    ################################################################################
    if RANK == 0:
        # plot_all(parameters,networkSim,PS,signal=True,morphology=True,position=True)
        plot_all(parameters, networkSim, PS, signal=True)

    COMM.Barrier()


if __name__ == '__main__':
    import os
    COMM = MPI.COMM_WORLD
    SIZE = COMM.Get_size()
    RANK = COMM.Get_rank()

    path_global = os.path.dirname(os.path.realpath(__file__))

    if not hasattr(neuron.h, 'ExpSynI'):
        # compile the exponential synapse which is not a default equation in neurons
        if RANK == 0:
            os.system('nrnivmodl')
        COMM.Barrier()
    pathes = [
        # path_global + '/../../data/local_cluster/case_up_down/',
        # path_global + '/../../data/local_cluster/case_asynchronous/',
        path_global + '/../../data/local_cluster/case_regular_burst/',
    ]
    for path in pathes:
        # generate_LFP(path, 'pop_1_', 44000.0, 44200.0, [0, 8000], [8000, 2000], name='/test/')
        generate_LFP(path, 'pop_1_', 41000.0, 43000.0, [0, 8000], [8000, 2000], name='/run/')
        # generate_LFP(path,'pop_1_',[0,  8000],[8000,  2000],name='/small_init_test_3/')
        # generate_LFP(path,'small_pop_2',[10000,  8000],[18000,  2000],name='/small_init/')
        # generate_LFP(path,'pop_1_',[0,  8000],[8000,  2000],name='/small_init_test_image/')
