#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import re
import os
import numpy as np

def select_spikes(begin, end, path_spikes, label, path_result):
    """
    selection of spike times from nest file
    :param begin: start analyse
    :param end: end analyse
    :param path_spikes: path of spike files
    :param label: label of population
    :param path_result: path of the result of the selection of spikes
    :return:
    """
    regex = re.compile(label + '\-\w*\-\w*\.dat')
    for root, dirs, files in os.walk(path_spikes):
        for file in files:
            if regex.match(file):
                data = np.asarray(np.genfromtxt(path_spikes+'/'+file,
                                                skip_header=2,
                                                skip_footer=0,
                                                names=True,
                                                dtype=None,
                                                delimiter='\t'))
                index = np.where(np.logical_and(data['time_ms'] >= begin, data['time_ms'] <= end))
                data['time_ms'] -= begin

                # get header
                header = ""
                with open(path_spikes+'/'+file, 'r') as f:
                    for i in range(3):
                        header += f.readline()
                    f.close()
                header = header[:-1]  # remove the last new line
                # save new file
                np.savetxt(path_result+'/'+file, data[index], header=header, comments='', fmt='%r\t%.3f')

if __name__ == '__main__':
    import os
    path_global = os.path.dirname(os.path.realpath(__file__))
    select_spikes(100, 200, path_global + '/../data/local_cluster/nest/',
                  'pop_1_ex',
                  path_global + '/../data/local_cluster/LFPY/test/pop_1_/spikes/')