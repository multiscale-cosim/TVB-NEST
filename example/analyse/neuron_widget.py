#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

def neuron_widget (nb_thread=4):
    import ipywidgets as ipw
    import nest
    import nest.raster_plot 

    import matplotlib.pylab as plt
    import numpy as np
    def model(N_ex=16,
              R_max_ex=150,
              f_ex=2,
              w_ex=0.3,
              E_ex=0.0,
              tau_syn_ex=5.0,
              p_ex=1.0,
              N_in=4,
              E_in=-80.0,
              tau_syn_in=5.0,
              R_max_in=150,
              f_in=15,
              w_in=-1.0,
              p_in=1.0,
              C_m=200.0,
              t_ref=5.0,
              g_L=10,
              E_L=--64.5,
              v_reset=-64.5,
              v_rheobase=-64.5,
              a=0.0,
              b=1.0,
              v_spike=10.,
              delta_T=2.0,
              tau_w=500.0,
              I_stim=0.0,
             duration = 20):
        nest.ResetKernel()
        nest.SetKernelStatus({"resolution": 0.001, "print_time": True,'local_num_threads': nb_thread})
        type_neuron = 'aeif_cond_alpha'
        params = {
                 'a': a,
                  'b': b,
                  'V_th': v_rheobase,
                  'Delta_T': delta_T,
                  'I_e': I_stim,
                  'C_m': C_m,
                  'g_L': g_L,
                  'V_reset': v_reset,
                  'tau_w': tau_w,
                  't_ref': t_ref,
                  'V_peak': v_spike,
                  'E_L': E_L,
                  'E_ex': E_ex,
                  'tau_syn_ex' : tau_syn_ex,
                  'E_in': E_in,
                  'tau_syn_in':tau_syn_in,
                  'gsl_error_tol':1e-06,
                  'V_m' : v_reset,
                  'w':0.0
        }
        neuron = nest.Create(type_neuron,1, params)

        # Simulation code
        G_ex = nest.Create("sinusoidal_poisson_generator",N_ex,
                           {'rate':R_max_ex*0.5,'amplitude':R_max_ex*0.5,'frequency':f_ex,'phase':0.0}) 
        G_in = nest.Create("sinusoidal_poisson_generator",N_in,
                           {'rate':R_max_in*0.5,'amplitude':R_max_in*0.5,'frequency':f_in,'phase':0.0}) 
        nest.CopyModel("static_synapse","excitatory",{"weight":w_ex})
        nest.Connect(G_ex,neuron,{'rule': 'pairwise_bernoulli', 'p': p_ex},syn_spec="excitatory")
        nest.CopyModel("static_synapse","inhibitory",{"weight":w_in})
        nest.Connect(G_in,neuron,{'rule': 'pairwise_bernoulli', 'p': p_in},syn_spec="inhibitory")
        # Run it
        nest.CopyModel("spike_recorder","sd_ex",{"record_to": 'memory'})
        MG_ex = nest.Create("sd_ex")
        nest.Connect(G_ex, MG_ex,syn_spec='static_synapse')
        nest.CopyModel("spike_recorder","sd_in",{"record_to": 'memory'})
        MG_in = nest.Create("sd_in")
        nest.Connect(G_in, MG_in,syn_spec='static_synapse')
        nest.CopyModel("spike_recorder","sd_n",{"record_to": 'memory'})
        MSH = nest.Create("sd_n")
        nest.Connect(neuron, MSH,syn_spec='static_synapse')
        MH = nest.Create("multimeter",params={"record_to": 'memory', "record_from":["V_m",'w']})
        nest.Connect(MH, neuron)
        nest.Simulate(duration)

        MG_ex_sim = nest.GetStatus(MG_ex,keys="events")[0]
        MG_in_sim = nest.GetStatus(MG_in,keys="events")[0]
        MSH_sim = nest.GetStatus(MSH,keys="events")[0]
        MH_sim = nest.GetStatus(MH)[0]


        # Plotting code
        plt.figure(figsize=(9, 4))
        plt.subplot(141)
        evs_ex = MG_ex_sim["senders"]
        ts_ex = MG_ex_sim["times"] 
        plt.plot(ts_ex, evs_ex,".")
        plt.title('Source excitatory neurons\n (sinusoidal Poisson generator)')
        plt.subplot(142)
        connection_ex=np.array(list(nest.GetConnections(G_ex,neuron).sources()))-G_ex.tolist()[0]
        plt.plot(np.zeros(N_ex), np.arange(N_ex), 'ob')
        plt.plot([0, 1], [connection_ex, np.ones(len(connection_ex))*N_ex/2.], '-k')
        plt.plot([1], [N_ex/2.], 'og')
        plt.xlim(-0.1, 1.1)
        plt.ylim(-1, N_ex)
        plt.axis('off')
        plt.title('Synapses\n excitatory')
        plt.subplot(143)
        evs_in = MG_in_sim["senders"]
        ts_in = MG_in_sim["times"]
        plt.plot(ts_in, evs_in,".")
        plt.title('Source inhibitory neurons\n (sinusoidal Poisson generator)')
        plt.subplot(144)
        connection_in=np.array(list(nest.GetConnections(G_in,neuron).sources()))-G_in.tolist()[0]
        plt.plot(np.zeros(N_in), np.arange(N_in), 'ob')
        plt.plot([0, 1], [connection_in, np.ones(len(connection_in))*N_in/2.], '-k')
        plt.plot([1], [N_in/2.], 'og')
        plt.xlim(-0.1, 1.1)
        plt.ylim(-1, N_in)
        plt.axis('off')
        plt.title('Synapses\n inhibitory')

        plt.figure(figsize=(9,6))
        plt.subplot(2, 2, 1)
        Vms = MH_sim["events"]["V_m"]
        ts = MH_sim["events"]["times"] 
        plt.plot(ts, Vms)
        plt.xlabel("t [ms]")
        plt.ylabel("u [mV]")
        plt.title("Membrane potential")
        plt.subplot(2, 2, 2)
        Vms = MH_sim["events"]["V_m"]
        ws = MH_sim["events"]["w"]
        plt.xlim(xmax = v_spike,xmin=np.min(np.array(Vms)))
        plt.plot(Vms,ws)
        plt.xlabel("u [mV]")
        plt.ylabel("w [pAmp]")
        plt.title("Phase plane representation")
        plt.subplot(2, 2, 3)
        Vms = MH_sim["events"]["w"]
        ts = MH_sim["events"]["times"] 
        plt.plot(ts, Vms)
        plt.xlabel("t [ms]")
        plt.ylabel("w [pAmp]")
        plt.title("Adaptation current")
        evs = MSH_sim["senders"]
        ts = MSH_sim["times"]
        plt.subplot(2, 2, 4)
        plt.plot(ts, evs,".")
        plt.title('Spike neurons')
        plt.xlabel("t [ms]")
        plt.subplots_adjust(hspace=0.8)
        plt.show()

    style = {'description_width': 'initial'}
    layout = ipw.Layout(width='100%', height='20px')
    ipw.interact(model,
                 N_ex=ipw.IntSlider(value=80, min=5, max=100, step=5, continous_update=False,
                                 description="N_ex = Number of source neurons", style=style,
                                   layout=layout),
                 R_max_ex=ipw.FloatSlider(value=150, min=0, max=500, step=10, continuous_update=False,
                                       description=r"Max_f_ex = Source neuron max firing rate (Hz)", style=style,
                                   layout=layout),
                 f_ex=ipw.FloatSlider(value=2, min=1, max=50, step=1, continuous_update=False,
                                   description=r"f_ex = Source neuron frequency (Hz)", style=style,
                                   layout=layout),
                 p_ex=ipw.FloatSlider(value=1, min=0, max=1, step=0.01, continuous_update=False,
                                   description=r"p_ex = Synapse probability", style=style,
                                   layout=layout),
                 w_ex=ipw.FloatSlider(value=0.3, min=0, max=1, step=0.01, continuous_update=False,
                                   description=r"w_syn_ex = Synapse weight", style=style,
                                   layout=layout),
                 E_ex=ipw.FloatSlider(value=0.0, min=-60.0, max=10.0, step=1.0, continuous_update=False,
                                   description=r"E_ex = Excitatory reversal potential in mV", style=style,
                                   layout=layout),
                 tau_syn_ex=ipw.FloatSlider(value=5.0, min=0.0, max=10.0, step=0.01, continuous_update=False,
                                   description=r"tau_syn_ex : Rise time of excitatory synaptic conductance in" 
                                           " ms (alpha function)", style=style,
                                   layout=layout),
                 N_in=ipw.IntSlider(value=20, min=5, max=100, step=5, continous_update=False,
                                 description="N_in = Number of source neurons", style=style,
                                   layout=layout),
                 R_max_in=ipw.FloatSlider(value=150, min=0, max=500, step=10, continuous_update=False,
                                       description=r"Max_f_in Source neuron max firing rate (Hz)", style=style,
                                   layout=layout),
                 f_in=ipw.FloatSlider(value=15, min=1, max=50, step=1, continuous_update=False,
                                   description=r"f_in = Source neuron frequency (Hz)", style=style,
                                   layout=layout),
                 p_in=ipw.FloatSlider(value=1, min=0, max=1, step=0.01, continuous_update=False,
                                   description=r"p_in = Synapse probability", style=style,
                                   layout=layout),
                 w_in=ipw.FloatSlider(value=-1.0, min=-1, max=0, step=0.01, continuous_update=False,
                                   description=r"w_syn_in = Synapse weight", style=style,
                                   layout=layout),
                 E_in=ipw.FloatSlider(value=-80.0, min=-100.0, max=0.0, step=1.0, continuous_update=False,
                                   description=r"E_in = Excitatory reversal potential in mV", style=style,
                                   layout=layout),
                 tau_syn_in=ipw.FloatSlider(value=5.0, min=0.0, max=10.0, step=0.01, continuous_update=False,
                                   description=r"tau_syn_in : Rise time of excitatory synaptic conductance in"
                                            " ms (alpha function)", style=style,
                                   layout=layout),
                 C_m=ipw.FloatSlider(value=200, min=0, max=500, step=10, continuous_update=False,
                                     description=r"C_m = Capacity of the membrane in pF ", style=style,
                                   layout=layout),
                 t_ref=ipw.FloatSlider(value=5.0, min=0.0, max=10.0, step=1.0, continuous_update=False,
                         description=r"t_ref : Duration of refractory period in ms", style=style,
                                   layout=layout),
                 g_L=ipw.FloatSlider(value=10, min=0.0, max=100, step=10, continuous_update=False,
                                       description=r"g_L = Leak conductance in nS", style=style,
                                   layout=layout),
                 E_L=ipw.FloatSlider(value=-64.5, min=-80.0, max=10.0, step=10, continuous_update=False,
                           description=r"E_l = reversal potential (mV)", style=style,
                                   layout=layout),
                 v_reset=ipw.FloatSlider(value=-64.5, min=-80.0, max=10.0, step=1, continuous_update=False,
                           description=r"Vr = voltage reset (mV)", style=style,
                                   layout=layout),
                 v_rheobase=ipw.FloatSlider(value=-64.5, min=-70.0, max=10.0, step=1, continuous_update=False,
                           description=r"Vt = threshold initialisation voltage (mV)", style=style,
                                   layout=layout),
                 a=ipw.FloatSlider(value=0.0, min=-5.0, max=5.0, step=0.1, continuous_update=False,
                           description=r"a = subthreshold adpatative (nS)", style=style,
                                   layout=layout),
                 b=ipw.FloatSlider(value=1.0, min=0.0, max=60.0, step=1.0, continuous_update=False,
                           description=r"b = spikke-triggered adaption(pA)", style=style,
                                   layout=layout),
                 v_spike=ipw.FloatSlider(value=10.0, min=-40.0, max=30.0, step=1.0, continuous_update=False,
                           description=r"V_peak = spike detection threshold(mV)", style=style,
                                   layout=layout),
                 delta_T=ipw.FloatSlider(value=2.0, min=0.0, max=10.0, step=1.0, continuous_update=False,
                           description=r"delta_T = slope factor(mV)", style=style,
                                   layout=layout),
                 tau_w=ipw.FloatSlider(value=500.0, min=0.0, max=1000.0, step=10.0, continuous_update=False,
                           description=r"tau_w = addaption time(ms)", style=style,
                                   layout=layout),
                 I_stim=ipw.FloatSlider(value=0.0, min=-20.0, max=20.0, step=1.0, continuous_update=False,
                           description=r"I_ext = external intensity (I)", style=style,
                                   layout=layout),
                 duration=ipw.FloatSlider(value=200.0, min=10.0, max=20000.0, step=10.0, continuous_update=False,
                           description=r"time simulation (ms)", style=style,
                                   layout=layout)
                )