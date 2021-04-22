#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import os

path = os.path.dirname(os.path.realpath(__file__)) + "/data_mouse/"

param_nest = {"sim_resolution": 0.1, "master_seed": 46, "total_num_virtual_procs": 3, "overwrite_files": True,
              "print_time": True, "verbosity": 20}
param_nest_topology = {"neuron_type": "aeif_cond_exp",
                       "param_neuron_excitatory": {"C_m": 200.0, "t_ref": 5.0, "V_reset": -64.5, "E_L": -64.5,
                                                   "g_L": 10.0, "I_e": 0.0, "a": 0.0, "b": 1.0, "Delta_T": 2.0,
                                                   "tau_w": 500.0, "V_th": -50.0, "E_ex": 0.0, "tau_syn_ex": 5.0,
                                                   "E_in": -80.0, "tau_syn_in": 5.0},
                       "param_neuron_inhibitory": {"C_m": 200.0, "t_ref": 5.0, "V_reset": -65.0, "E_L": -65.0,
                                                   "g_L": 10.0, "I_e": 0.0, "a": 0.0, "b": 0.0, "Delta_T": 0.5,
                                                   "tau_w": 1.0, "V_th": -50.0, "E_ex": 0.0, "tau_syn_ex": 5.0,
                                                   "E_in": -80.0, "tau_syn_in": 5.0}, "mean_I_ext": 0.0,
                       "sigma_I_ext": 0.0, "sigma_V_0": 10.0, "mean_w_0": 10.0,
                       "nb_region": 104, "nb_neuron_by_region": 1000, "percentage_inhibitory": 0.2}
param_nest_connection = {"weight_local": 1.0, "g": 5.0, "p_connect": 0.05, "weight_global": 1.0,
                         "nb_external_synapse": 115, "path_weight": path + '/weights.npy',
                         "path_distance": path + '/distance.npy', "velocity": 3.0}
param_nest_background = {"poisson": True, "rate_ex": 2.0, "rate_in": 0.0, "weight_poisson": 1.0,
                         "noise": False,
                         "stimulus": False,
                         "multimeter": True,
                         "multimeter_list": {"pop_1_ex_VM": [["V_m"], 0, 10], "pop_1_ex_W": [["w"], 0, 10],
                                             "pop_1_in_VM": [["V_m"], 800, 810], "pop_1_in_W": [["w"], 800, 810]},
                         "record_spike": True,
                         "record_spike_list": {"pop_1_ex": [0, 800], "pop_2_ex": [1000, 1799], "pop_1_in": [800, 999],
                                               "pop_2_in": [1800, 1999]}}
param_tvb_model = {"order": 2,
                   "T": 20.0,
                   "P_e": [-0.05059317, 0.0036078, 0.01794401, 0.00467008, 0.00098553, 0.0082953, -0.00985289,
                           -0.02600252, -0.00274499, -0.01051463],
                   "P_i": [-0.0596722865, 0.00715675508, 0.00428252163, 0.00925089702, 1.16632197e-06, -0.010065931,
                           0.00389257235, 0.000445787751, 0.00420050937, 0.00437359879],
                   'tau_OU': 5.0, 'weight_noise': 10.5*1e-5,
                   "initial_condition": {
                       "E": [0.0, 0.0], "I": [0.0, 0.0], "C_ee": [0.0, 0.0], "C_ei": [0.0, 0.0],
                       "C_ii": [0.0, 0.0], "W_e": [5.0, 0.0], "W_i": [0.0, 0.0]},
                   "g_L": 10.0, "E_L_e": -64.5, "E_L_i": -65.0, "C_m": 200.0,
                   "b_e": 1.0, "a_e": 0.0, "b_i": 0.0, "a_i": 0.0, "tau_w_e": 500.0, "tau_w_i": 1.0,
                   "E_e": 0.0, "E_i": -80.0, "Q_e": 1.0, "Q_i": 5.0, "tau_e": 5.0, "tau_i": 5.0,
                   "N_tot": 1000, "p_connect_e": 0.05, "p_connect_i": 0.05, "g": 0.2, "K_ext_e": 115}
param_tvb_connection = {"path_region_labels": path + '/region_labels.txt',
                        "path_centers": path + '/centres.txt',
                        "path_cortical": path + "/cortical.npy",
                        "orientation": True,
                        "path_distance": path + '/distance.npy',
                        "path_weight": path + '/weights.npy',
                        "nb_region": 104,
                        "velocity": 3.0}
param_tvb_coupling = {"a": 1.0}
param_tvb_integrator = {"sim_resolution": 0.1, "seed": 45, "seed_init": 44}
param_tvb_monitor = {"save_time": 20.0,
                     "Raw": True,
                     "TemporalAverage": False,
                     "parameter_TemporalAverage": {"variables_of_interest": [0, 1, 2, 3], "period": 1.0},
                     "Bold": False,
                     "parameter_Bold": {"variables_of_interest": [0], "period": 2000.0},
                     "ECOG": True,
                     "parameter_ECOG": {"path": path + '/sensor_hypocampus.txt', "scaling": 1.e3}}
param_TR_nest_to_tvb = {"resolution": 0.1, "nb_neurons": 800.0, "synch": 2.0, "width": 20.0, "level_log": 1,
                        'save_hist': True, 'save_hist_count': 50,
                        'save_rate': True, 'save_rate_count': 50}
param_TR_tvb_to_nest = {"percentage_shared": 0.5, "level_log": 1, "seed": 43, "nb_synapses": 115,
                        'function_select': 2,
                        'save_spike': True, 'save_spike_count': 50,
                        'save_rate': True, 'save_rate_count': 50}
param_co_simulation = {"co-simulation": True, "nb_MPI_nest": 1,
                       "record_MPI": False, "id_region_nest": [26, 78],
                       "synchronization": 2.0,
                       "level_log": 1,
                       "mpi": ['mpirun'],
                       'translation_thread': False}
begin = 0.0
end = 2000.0
