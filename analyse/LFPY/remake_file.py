import h5py
import numpy as np


for folder in [#'case_asynchronous',
               'case_regular_burst', 'case_up_down']:
    path ='/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/data/local_cluster/' + folder
    f_run = h5py.File(path + '/LFPY/run/pop_1_/RecExtElectrode_sum.h5', 'r')
    data = np.mean(f_run['data'][:, :-1].reshape(32, 2000, 10), axis=2)[:, :-501]
    f_v2 = h5py.File(path + '/LFPY/v2/pop_1_/RecExtElectrode_sum.h5', 'r')
    data = np.concatenate([data, f_v2['data'][:, :]], axis=1)

    f_new = h5py.File(path + '/LFPY/RecExtElectrode_sum.h5', 'w')
    f_new.create_dataset("data", data=data)
    f_new.create_dataset("srate", data=f_v2['srate'][()])
    f_new.close()