#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

'''
spike detector with mpi backend
'''

import nest
import numpy
import os

nest.ResetKernel()
# Set parameter of kernel. The most important is the set of the path
nest.SetKernelStatus({"overwrite_files": True,
                      "data_path": os.path.dirname(os.path.realpath(__file__)) + "/../test_nest_spike_multi/",
                      "total_num_virtual_procs": 4,
                      })
# Creation of neurons
n = nest.Create("iaf_psc_alpha",
                params={"tau_syn_ex": 1.0, "V_reset": -70.0})
n_2 = nest.Create("iaf_psc_alpha",
                  params={"tau_syn_ex": 2.0, "V_reset": -70.0})
# creation of spike detector with MPI
m = nest.Create("spike_recorder",
                params={
                    "record_to": "mpi",
                    "label": "./"})
m_2 = nest.Create("spike_recorder",
                  params={
                      "record_to": "mpi",
                      "label": "./"})
# Creation of spike generator
s_ex = nest.Create("spike_generator",
                   params={"spike_times": numpy.array([10.0, 20.0, 50.0])})
s_in = nest.Create("spike_generator",
                   params={"spike_times": numpy.array([15.0, 25.0, 55.0])})
# Creation of current generator
dc = nest.Create("dc_generator",
                 params={"amplitude": 900.0})
dc_2 = nest.Create("dc_generator",
                   params={"amplitude": 1000.0})
print("create nodes")
# Creation of connections
nest.Connect(s_ex, n, syn_spec={"weight": 100.0})
nest.Connect(s_in, n, syn_spec={"weight": 0.0})
nest.Connect(dc, n)
nest.Connect(dc_2, n_2)
nest.Connect(n, m)
nest.Connect(n_2, m_2)
print("create connect")

'''
A network simulation with a duration of 5*100 ms is started.
'''
print("Spike detector 1 {} and 2 {}".format(n, n_2))
nest.Prepare()
nest.Run(200.)
nest.Run(200.)
nest.Run(200.)
nest.Run(200.)
nest.Cleanup()
