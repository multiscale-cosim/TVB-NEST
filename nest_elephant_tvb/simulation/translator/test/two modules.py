from translator.rate_spike import rates_to_spikes,spikes_to_rate
from quantities import ms,s, Hz
import numpy as np
import numpy.random as rgn

#test one rate
rgn.seed(42)
rate = 10*Hz
t_start = 0.0*s
t_stop = 1000.0*s
precision = 1.0
max_diff = 0.0
for i in range(1000):
    spike = rates_to_spikes(rate,t_start=t_start,t_stop=t_stop)
    rate_test = spikes_to_rate(spike*ms,t_start=t_start,t_stop=t_stop)
    if rate_test*Hz - rate >= precision:
        print('FAIL test')
        print(rate_test)
        i=-1
        break
    else:
        if rate_test*Hz - rate > max_diff:
            max_diff = rate_test*Hz - rate

if i != -1:
    print('test succeeds')
    print("precision :%r"%max_diff[0])


#test multiple rates
rgn.seed(42)
rate = [10,100,5,50]*Hz
t_start = 0.0*s
t_stop = 1000.0*s
precision = 1.0
max_diff = 0.0
for i in range(1000):
    spike = rates_to_spikes(rate,t_start=t_start,t_stop=t_stop)
    rate_test = spikes_to_rate(spike*ms,t_start=t_start,t_stop=t_stop)
    if np.min(rate_test*Hz - rate) >= precision:
        print('FAIL test')
        print(rate_test)
        i=-1
        break
    else:
        if np.max(rate_test*Hz - rate) > max_diff:
            max_diff = np.max(rate_test*Hz - rate)

if i != -1:
    print('test succeeds')
    print("precision :%r"%max_diff)