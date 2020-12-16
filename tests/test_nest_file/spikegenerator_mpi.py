#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

'''
spike generator with mpi backend
'''

import nest
import numpy
import os

nest.ResetKernel()
# Set parameter of kernel. The most important is the set of the path
nest.SetKernelStatus({"overwrite_files": True,
                      "data_path": os.path.dirname(os.path.realpath(__file__))+"/../",
                      })
# Creation of neurons
n = nest.Create("iaf_psc_alpha",
                params={"tau_syn_ex": 1.0, "V_reset": -70.0})
n_2 = nest.Create("iaf_psc_alpha",
                params={"tau_syn_ex": 2.0, "V_reset": -70.0})
# creation of spike detector with MPI or not
m = nest.Create("spike_recorder",
                params={
                        "record_to": "mpi",
                        "label": "test_nest_spike"})
m_2 = nest.Create("spike_recorder",
                params={
                    "record_to": "mpi",
                    "label":"test_nest_spike"})
m_3 = nest.Create("spike_recorder",
                  params={
                      "record_to": "memory",
                      "label":"test_nest_spike"})
m_4 = nest.Create("spike_recorder",
                  params={
                      "record_to": "memory",
                      "label":"test_nest_spike"})
# Creation of spike generator with MPI or not
s_ex = nest.Create("spike_generator",
                   params={"spike_times": numpy.array([]),
                           'stimulus_source':'mpi',
                           "label":"test_nest_spike"})
s_in = nest.Create("spike_generator",
                   params={"spike_times": numpy.array([15.0, 25.0, 55.0])})
# Creation of current generator
dc = nest.Create("dc_generator",
                 params={"amplitude":900.0})
dc_2 = nest.Create("dc_generator",
                 params={"amplitude":1000.0})
print("create nodes")
# Creation of connections
nest.Connect(s_ex, n, syn_spec={"weight": 1000.0})
nest.Connect(s_in, n_2, syn_spec={"weight": 1000.0})
nest.Connect(n,m)
nest.Connect(n_2,m)
nest.Connect(s_ex,m_2)
nest.Connect(s_in,m_2)
nest.Connect(n,m_3)
nest.Connect(n_2,m_3)
nest.Connect(s_ex,m_4)
nest.Connect(s_in,m_4)
print("create connect")

'''
A network simulation with a duration of 5*100 ms is started.
'''
print("Spike generator 1 {} and 2 {}".format(s_in, s_ex))
nest.Prepare()
print("Start run")
nest.Run(200.)
nest.Run(200.)
nest.Run(200.)
nest.Run(200.)
nest.Cleanup()
# print result
print(nest.GetStatus(m_3)[0]['events'])
print(nest.GetStatus(m_4)[0]['events'])

