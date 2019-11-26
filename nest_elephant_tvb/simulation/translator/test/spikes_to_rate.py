from translator.rate_spike import spikes_to_rate
from quantities import ms
import numpy as np
import numpy.random as rgn

# #test one spiketrain
# rgn.seed(42)
# t_start = 0.0
# t_stop = 1000.0
# rate_wanted = 10
# save = []
#
# for i in range(1000):
#     spike = rgn.uniform(0.0, 1000.0, rate_wanted)
#     rate = spikes_to_rate(spike*ms,t_start=t_start*ms,t_stop=t_stop*ms)
#     save.append(rate[0])
#
# if np.around(np.mean(save)) == rate_wanted:
#     print('test succeeds')
# else:
#     print('FAIL test')
#     print(np.mean(save))
#     print(save)
#
# #test multy spiketrain
# rgn.seed(42)
# t_start = 0.0
# t_stop = 1000.0
# rate_wanted = [10,5,6,100]
# save = []
#
# for i in range(1000):
#     spike = []
#     for rate in rate_wanted:
#         spike.append(rgn.uniform(0.0, 1000.0, rate))
#     rate = spikes_to_rate(spike*ms,t_start=t_start*ms,t_stop=t_stop*ms)
#     save.append(rate)
#
# if (np.around(np.mean(save,axis=0)) == rate_wanted).all():
#     print('test succeeds')
# else:
#     print('FAIL test')
#     print(np.mean(save))
#     print(save)

#test one spiketrain with windows
rgn.seed(42)
t_start = 0.0
t_stop = 1000.0
rate_wanted = 10
save = []

for i in range(1000):
    spike = rgn.uniform(0.0, 1000.0, rate_wanted)
    rate = spikes_to_rate(spike*ms,t_start=t_start*ms,t_stop=t_stop*ms,windows=100.0*ms)
    save.append(rate[0])

if np.around(np.mean(save)) == rate_wanted:
    print('test succeeds')
else:
    print('FAIL test')
    print(np.mean(save))
    print(save)


#test multy spiketrain with windows
rgn.seed(42)
t_start = 0.0
t_stop = 1000.0
rate_wanted = [10,5,6,100]
save = []

for i in range(1000):
    spike = []
    for rate in rate_wanted:
        spike.append(rgn.uniform(0.0, 1000.0, rate))
    rate = spikes_to_rate(spike*ms,t_start=t_start*ms,t_stop=t_stop*ms,windows=100.0*ms)
    save.append(rate)

if (np.around(np.mean(save,axis=(0,1))) == rate_wanted).all():
    print('test succeeds')
else:
    print('FAIL test')
    print(np.mean(save,axis=0))
    print(save)

#test one spiketrain with windows and variation
rgn.seed(42)
t_start = 0.0
t_stop = 2000.0
rate_wanted = [10,20]
save = []

for i in range(1000):
    spike = np.concatenate((rgn.uniform(0.0, 1000.0, rate_wanted[0]),rgn.uniform(1000.0, 2000.0, rate_wanted[1])))
    rate = spikes_to_rate(spike*ms,t_start=t_start*ms,t_stop=t_stop*ms,windows=100.0*ms)
    save.append(rate)
save = np.swapaxes(save,0,1)
if [np.around(np.mean(save[0:9])),np.around(np.mean(save[10:19]))] == rate_wanted:
    print('test succeeds')
else:
    print('FAIL test')
    print(np.mean(save))
    print(save)

#test multy spiketrain with windows and variation
rgn.seed(42)
t_start = 0.0
t_stop = 2000.0
rate_wanted = [[10,50],
                [5,6],
                [1,100],
               [100,1]]
save = []

for i in range(1000):
    spike = []
    for rate in rate_wanted:
        spike.append(np.concatenate((rgn.uniform(0.0, 1000.0, rate[0]),rgn.uniform(1000.0, 2000.0, rate[1]))))
    rate = spikes_to_rate(spike*ms,t_start=t_start*ms,t_stop=t_stop*ms,windows=100.0*ms)
    save.append(rate)

save = np.swapaxes(save,0,1)
if [np.around(np.mean(save[0:9],axis=(0,1))),np.around(np.mean(save[10:19],axis=(0,1)))] == rate_wanted:
    print('test succeeds')
else:
    print('FAIL test')
    print(np.mean(save,axis=0))
    print(save)