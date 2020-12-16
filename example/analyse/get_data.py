#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import csv
import numpy as np
import os
import re

# import data generate by Nest
def import_data_file(path):
    """
    import data from one recorder of nest
    :param path: file with data saved by Nest
    :return: data from one file
    """
    data =np.asarray(np.genfromtxt(path,
                     skip_header=2,
                     skip_footer=0,
                     names=True,
                     dtype=None,
                     delimiter='\t'))
    if len(data.shape) == 0:
        data.reshape((1,))
    return data

def get_label_and_type(path,nb):
    """
    get the description of type of recording and the name of the file
    :param path: file with all information record
    :param nb: index of the population
    :return: the label and the type of the recordinng data
    """
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
    """
    the number of label
    :param path: the path to the files with labels
    :return:
    """
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        nb_label = sum(1 for row in csv_reader )
    return nb_label-1 # remove header

def get_data(label,path):
    """
    collect all the data from one record, concatenate them and return them
    :param label: the label of the recorder
    :param path: the folder of recorded file
    :return: data of the recorder
    """
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
           if len(data[name].shape) == 0:
                data_concatenate[i]=np.concatenate((data_concatenate[i],[data[name]]))
           else:
               data_concatenate[i] = np.concatenate((data_concatenate[i], data[name]))
    return field,np.array(data_concatenate)

def reorder_data_multimeter(data):
    """
    Order the data of multimeter
    The order in input are by time, by neurons, by value in contiguous value
    The order in output are by neurons, by times, by value in different dimensions
    :param data: the reorder data
    :return:
    """
    ids = np.unique(data[0]) # give id of neurons
    time = np.unique(data[1]) # give time
    index_ids = np.argsort(data[0])
    index_time = np.argsort(data[1][index_ids])
    value =[]
    for i in range(2,len(data)):
        value.append(np.swapaxes(np.reshape(data[i][index_ids][index_time],(time.shape[0],ids.shape[0])),0,1))
    return [ids,time,np.concatenate(value)]

def reorder_data_spike_detector(data):
    """
    Order data of spike recorder
    The order in input are by time and neurons in contiguous value
    The order in output are by neurons and by time in different dimension
    :param data: the reorder data
    :return:
    """
    ids = np.unique(data[0])
    spikes =[]
    for i in ids:
        spikes.append(data[1][np.where(data[0] == i )])
    return [ids,np.array(spikes)]

def get_data_all(path):
    """
    Get all data of Nest and reorder them.
    :param path: the path of the Nest folder
    :return:
    """
    nb = count_number_of_label(path+ 'labels.csv')
    data_pop = {}
    for i in range(nb):
        label, type = get_label_and_type(path + 'labels.csv', i)
        field, data = get_data(label, path)
        if type == 'spikes':
            data_pop[label]=reorder_data_spike_detector(data)
        else:
            data_pop[label]=reorder_data_multimeter(data)
    return data_pop

# import data generate by TVB
def get_rate(path):
    '''
    return the result of the simulation from TVB
    :param path: the folder of TVB
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

if __name__ == '__main__':
    path = '../../example/long_simulation/'
    data_pop = get_data_all(path+'/nest/')
    print(len(data_pop))
    print(data_pop.keys())
    rate = get_rate(path+'/tvb/')
    import matplotlib.pyplot as plt
    plt.figure()
    for i in range(75,79,1):
        plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,i,:]*1e3,label=str(i))
    plt.legend()
    plt.figure()
    plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,77,:]*1e3)
    plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,25,:]*1e3)
    plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,2,:]*1e3)
    plt.figure()
    plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,0,:,0]*1e3)
    plt.figure()
    plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,1,:,0]*1e3)
    plt.figure()
    plt.plot(rate[0][0],np.concatenate(rate[0][1]).reshape(rate[0][1].shape[0],7,104,1)[:,5,:,0])
    plt.show()



