# -*- coding: utf-8 -*-
#
# multimeter_file.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

'''
Multimeter to file example
--------------------------

This file demonstrates recording from an `iaf_cond_alpha` neuron using a
multimeter and writing data to file.
'''

'''
First, the necessary modules for simulation and plotting are imported.

The simulation kernel is put back to its initial state using `ResetKernel`.
'''

import nest
import numpy
import sys
import os

nest.ResetKernel()

'''
With `SetKernelStatus`, global properties of the simulation kernel can be
specified. The following properties are related to writing to file:

* `overwrite_files` is set to True to permit overwriting of an existing file.
* `data_path` is the path to which all data is written. It is given relative to
  the current working directory.
* 'data_prefix' allows to specify a common prefix for all data files.
'''

nest.SetKernelStatus({"overwrite_files": True,
                      "data_path": os.path.dirname(os.path.realpath(__file__))+"/../",
                      "total_num_virtual_procs":4,
                      })

'''
For illustration, the recordables of the `iaf_cond_alpha` neuron model are
displayed. This model is an implementation of a spiking neuron using
integrate-and-fire dynamics with conductance-based synapses. Incoming spike
events induce a post-synaptic change of conductance modelled by an alpha
function.
'''

print("iaf_psc_alpha recordables: {0}".format(
      nest.GetDefaults("iaf_psc_alpha")["recordables"]))

'''
A neuron, a multimeter as recording device and two spike generators for
excitatory and inhibitory stimulation are instantiated. The command `Create`
expects a model type and, optionally, the desired number of nodes and a
dictionary of parameters to overwrite the default values of the model.

* For the neuron, the rise time of the excitatory synaptic alpha function
  in ms `tau_syn_ex` and the reset potential of the membrane in mV `V_reset`
  are specified.
* For the multimeter, the time interval for recording in ms `interval` and a
  selection of measures to record (the membrane voltage in mV `V_m` and the
  excitatory `g_ex` and inhibitoy `g_in` synaptic conductances in nS) are set.

  In addition, more parameters can be modified for writing to file:

  - `record_to` indicates where to put recorded data. All possible values are
    available by typing `nest.GetKernelStatus("recording_backends").keys()`.
  - `label` specifies an arbitrary label for the device. It is used instead of
    the name of the model in the output file name.

* For the spike generators, the spike times in ms `spike_times` are given
  explicitly.
'''

n = nest.Create("iaf_psc_alpha",
                params={"tau_syn_ex": 1.0, "V_reset": -70.0})
n_2 = nest.Create("iaf_psc_alpha",
                params={"tau_syn_ex": 2.0, "V_reset": -70.0})

m = nest.Create("spike_detector",
                  params={
                      "record_to": "memory"
                  })

s_ex = nest.Create("step_current_generator",
                   params={"amplitude_times": numpy.array([]),
                           "amplitude_values": numpy.array([]),
                           'input_from':'mpi',
                           "label":"test_nest_current_multi"})
s_in = nest.Create("step_current_generator",
                   params={
                       "amplitude_times": numpy.array([1.0, 100.0, 400.0]),
                       "amplitude_values": numpy.array([-15.0, -25.0, -55.0])})

'''
Next, the spike generators are connected to the neuron with `Connect`. Synapse
specifications can be provided in a dictionary. In this example of a
conductance-based neuron, the synaptic weight `weight` is given in nS.
Note that it is positive for excitatory and negative for inhibitory
connections.
'''

nest.Connect(s_ex, n, syn_spec={"weight": 1000.0})
nest.Connect(s_in, n_2, syn_spec={"weight": 1000.0})
nest.Connect(n,m)
nest.Connect(n_2,m)
nest.Connect(s_ex,n)
nest.Connect(s_in,n_2)

'''
A network simulation with a duration of 100 ms is started with `Simulate`.
'''
print("Spike generator 1 {} and 2 {}".format(s_in, s_ex))
nest.Prepare()
nest.Run(200.)
# time.sleep(10.)
nest.Run(200.)
# time.sleep(10.)
nest.Run(200.)
# time.sleep(10.)
nest.Run(200.)
# time.sleep(10.)
nest.Cleanup()
# nest.Simulate(200.)
print(nest.GetStatus(m)[0]['events'])


