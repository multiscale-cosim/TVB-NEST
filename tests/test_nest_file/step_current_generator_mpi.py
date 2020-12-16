#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

'''
step current generator with mpi backend
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
                params={"tau_syn_ex": 1.0, "V_reset": -70.0})
# creation of spike detector with MPI or not
m = nest.Create("spike_recorder",
                  params={
                      "record_to": "memory"
                  })
# Creation of current generator with MPI or not
s_ex = nest.Create("step_current_generator",
                   params={"amplitude_times": numpy.array([]),
                           "amplitude_values": numpy.array([]),
                           'stimulus_source':'mpi',
                           "label":"test_nest_current"})
s_in = nest.Create("step_current_generator",
                   params={
                       "amplitude_times": numpy.array([1.0, 100.0, 400.0]),
                       "amplitude_values": numpy.array([-15.0, -25.0, -55.0])})
print("create nodes")
# Creation of connections
nest.Connect(n,m)
nest.Connect(n_2,m)
nest.Connect(s_ex,n)
nest.Connect(s_in,n_2)
nest.Connect(s_ex,n_2)
print("create connect")

'''
A network simulation with a duration of 100 ms is started.
'''
print("Spike generator 1 {} and 2 {}".format(s_in, s_ex))
nest.Prepare()
nest.Run(200.)
nest.Run(200.)
nest.Run(200.)
nest.Run(200.)
nest.Cleanup()
# print result
print(nest.GetStatus(m)[0]['events'])


