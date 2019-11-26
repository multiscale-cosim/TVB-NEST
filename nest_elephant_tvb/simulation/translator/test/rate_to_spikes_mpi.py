from translator.rate_spike import rates_to_spikes
from quantities import s, Hz
import numpy as np
import numpy.random as rgn

#test one rate
rgn.seed(42)
rate = 10*Hz
save = []

for i in range(1000):
    spike = rates_to_spikes(rate,t_start=0.0*s,t_stop=1.0*s)
    save.append(len(spike[0]))

if np.around(np.mean(save)) == 10.0:
    print('test succeeds')
else:
    print('FAIL test')
    print(np.mean(save))

#test multy rate
rgn.seed(42)
rates = np.array([5,3,4,100,10])
save = []

for i in range(1000):
    spikes = rates_to_spikes(rates* Hz, t_start=0.0 * s, t_stop=1.0 * s)
    len_spike = []
    for spike in spikes:
        len_spike.append(len(spike))
    save.append(np.array(len_spike))

if (np.around(np.mean(save,axis=0)) == rates).all():
    print('test succeeds')
else:
    print('FAIL test')
    print(np.mean(save))

#test variation in rate
rgn.seed(42)
rates = np.array([100,3,4,3,100])
save = []

for i in range(1000):
    spikes = rates_to_spikes(rates* Hz, t_start=0.0 * s, t_stop=1.0 * s, variation=True)
    len_spike = []
    for spike in spikes:
        len_spike.append(len(spike))
    save.append(np.array(len_spike))
if (np.around(np.mean(save,axis=0)) == np.around(np.mean(rates))).all():
    print('test succeeds')
else:
    print('FAIL test')


#test variation in rate
rgn.seed(42)
rates = np.array([[3,3,3,3,3],
                  [100,3,4,3,100]])
save = []

for i in range(1000):
    spikes = rates_to_spikes(rates* Hz, t_start=0.0 * s, t_stop=1.0 * s, variation=True)
    len_spike = []
    for spike in spikes:
        len_spike.append(len(spike))
    save.append(np.array(len_spike))

if (np.around(np.mean(save,axis=0)) == np.around(np.mean(rates,axis=1))).all():
    print('test succeeds')
else:
    print('FAIL test')
    print(np.around(np.mean(save,axis=0)))
    print(np.around(np.mean(rates,axis=0)))
