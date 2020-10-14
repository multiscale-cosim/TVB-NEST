import logging
import numpy as np

def create_logger(path,name):
    """
    creatae the logger for the different part of the test
    :param path: path of files
    :param name: name of the testing part
    :return:
    """
    # Configure logger
    logger = logging.getLogger(name)
    fh = logging.FileHandler(path+name+'.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    fh.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    return logger

def generate_spike(seed,nb_run,time_sim,size_shape=100):
    """
    generator of spike shared between the configuration of nest and the mpi input
    :param seed: seed of the generator / the index of the device
    :param nb_run: number of run
    :param time_sim: the time of 1 run
    :param size_shape:  maximum size of the shape
    :return:
    """
    np.random.seed(seed)
    shapes = []
    datas = []
    for i in range(nb_run):
        shape = np.random.randint(0, size_shape, 1, dtype='i')[0]
        shapes.append(shape)
        data = time_sim*i + np.random.rand(shape) * time_sim # random time of spike during the time
        datas.append(np.around(np.sort(np.array(data, dtype='d')), decimals=1).tolist())
    return (shapes,datas)

def generate_current(seed,nb_run,time_sim,size_shape=100):
    np.random.seed(seed)
    shapes = []
    datas = []
    for i in range(nb_run):
        shape = np.random.randint(0, size_shape, 1, dtype='i')[0]
        shapes.append(shape*2)
        times = time_sim*i + np.random.rand(shape) * time_sim # random time of spike during the time
        times = np.around(np.sort(np.array(times, dtype='d')), decimals=1)
        index = np.where(np.diff(times)==0)[0]+1
        while len( index ) != 0: # avoid to have two times the time
            times[index]+=0.1
            index = np.where(np.diff(times)==0)[0]+1
        data  = np.random.rand(shape) * time_sim # define the current change
        datas.append(np.array(([[times[i], data[i]] for i in range(shape)])))
    return shapes, datas
