import csv
import numpy as np
import os
import re

def import_data_file(path):
    data =np.asarray(np.genfromtxt(path,
                     skip_header=2,
                     skip_footer=0,
                     names=True,
                     dtype=None,
                     delimiter='\t'))
    return data

def get_label_and_type(path,nb):
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                if line_count == nb+1:
                    return (row[0],row[1])
                line_count += 1
        raise Exception('not enough number of line')

def count_number_of_label(path):
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        nb_label = sum(1 for row in csv_reader )
    return nb_label-1 # remove header

def get_data(label,path):
    regex = re.compile(label+'\-\w*\-\w*\.dat')
    data_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if regex.match(file):
                data = import_data_file(path+file)
                if data.shape != 0:
                    data_list.append(data)
    field =  data_list[0].dtype.names
    data_concatenate = [[] for i in field ]
    for data in data_list:
       for i,name in enumerate(field):
           data_concatenate[i]=np.concatenate((data_concatenate[i],data[name]))
    return field,np.array(data_concatenate)

def reorder_data_multimeter(data):
    ids = np.unique(data[0]) # give id of neurons
    time = np.unique(data[1]) # give time
    index_ids = np.argsort(data[0])
    index_time = np.argsort(data[1][index_ids])
    value =[]
    for i in range(2,len(data)):
        value.append(np.swapaxes(np.reshape(data[i][index_ids][index_time],(time.shape[0],ids.shape[0])),0,1))
    return [ids,time,np.concatenate(value)]

def reorder_data_spike_detector(data):
    ids = np.unique(data[0])
    spikes =[]
    for i in ids:
        spikes.append(data[1][np.where(data[0] == i )])
    return [ids,np.array(spikes)]

def get_data_all(path):
    nb = count_number_of_label(path+ 'labels.csv')
    data_pop = []
    for i in range(nb):
        label, type = get_label_and_type(path + 'labels.csv', i)
        field, data = get_data(label, path)
        if type == 'spikes':
            data_pop.append(reorder_data_spike_detector(data))
        else:
            data_pop.append(reorder_data_multimeter(data))
    return data_pop

def get_rate(path):
    '''
    return the result of the simulation between the wanted time
    :param path: the folder of the simulation
    :param time_begin: the start time for the result
    :param time_end:  the ending time for the result
    :return: result of all monitor
    '''
    count = 0
    output = None
    while os.path.exists(path+'/step_'+str(count)+'.npy'):
        result = np.load(path + '/step_' + str(count) + '.npy', allow_pickle=True)
        if output is None:
            output = [ None for i in range(result.shape[0])]
        for i in range(result.shape[0]):
            data = np.array(result[i])
            if data.shape[0] != 0:
                if output[i] is None:
                    output[i] = [None for j in range(data.shape[1]) ]
                for j in range(data.shape[1]):
                    if output[i][j] is None:
                        output[i][j] =  data[:,j]
                    else:
                        output[i][j] = np.concatenate((output[i][j], data[:,j]))
        count+=1
    return output

# path = '/home/kusch/Documents/project/co_simulation/co-simulation-tvb-nest/test_nest/test_co-sim/_g_5.0_mean_I_ext_0.0/'
# # data_pop = get_data_all(path+'/nest/')
# # print(len(data_pop))
# rate = get_rate(path+'/tvb/')
# import matplotlib.pyplot as plt
# plt.figure()
# # for i in range(75,79,1):
# #     plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,i,:]*1e3,label=str(i))
# plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,77,:]*1e3)
# plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,25,:]*1e3)
# plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,2,:]*1e3)
# plt.legend()
# plt.figure()
# plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,:,0]*1e3)
# plt.figure()
# plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,1,:,0]*1e3)
# plt.figure()
# plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,5,:,0])
# plt.show()



