import numpy as np
import copy
import logging

def slidding_window(data,width):
    """
    use for mean field
    :param data: instantaneous firing rate
    :param width: windows or times average of the mean field
    :return: state variable of the mean field
    """
    res = np.zeros((data.shape[0]-width,width))
    res [:,:] = data[[[ i+j for i in range(width) ] for j in range(data.shape[0]-width)]]
    return res.mean(axis=1)

class store_data:
    def __init__(self,path,param):
        """
        initialisation
        :param path : path for the logger files
        :param param : parameters for the object
        """
        self.synch=param['synch']                # time of synchronization between 2 run
        self.dt=param['resolution']              # the resolution of the integrator
        self.shape = (int(self.synch/self.dt),1) # the shape of the buffer/histogram
        self.hist = np.zeros(self.shape)         # the initialisation of the histogram

        # configuration of the logger
        level_log = param['level_log']
        self.logger = logging.getLogger('store')
        fh = logging.FileHandler(path+'/nest_to_tvb_science.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        if level_log == 0:
            fh.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
        elif  level_log == 1:
            fh.setLevel(logging.INFO)
            self.logger.setLevel(logging.INFO)
        elif  level_log == 2:
            fh.setLevel(logging.WARNING)
            self.logger.setLevel(logging.WARNING)
        elif  level_log == 3:
            fh.setLevel(logging.ERROR)
            self.logger.setLevel(logging.ERROR)
        elif  level_log == 4:
            fh.setLevel(logging.CRITICAL)
            self.logger.setLevel(logging.CRITICAL)

    def add_spikes(self,count,datas):
        """
        adding spike in the histogram
        :param count: the number of synchronization times
        :param data: the spike :(id,time)
        """
        for data in np.reshape(datas,(int(datas.shape[0]/3),3)):
            data[2]-=self.dt
            self.hist[int((data[2]-count*self.synch)/self.dt)]+=1
        self.logger.info(int(datas.shape[0]/3))

    def return_data(self):
        """
        return the histogram and reinitialise the histogram
        :return: histogram
        """
        hist_copy = copy.copy(self.hist)
        self.hist = np.zeros(self.shape) # initialise histogram histogram of one region
        return hist_copy

class analyse_data:
    def __init__(self,path,param):
        """
        initialisation
        :param path : the path for saving the logger file
        :param param : the parameters of analysis
        """

        self.width = int(param['width']/param['resolution']) # the window of the average in time
        self.synch = param['synch']                          # synchronize time between simulator
        self.buffer = np.zeros((self.width,))                  #initialisation/ previous result for a good result
        self.coeff = 1 / ( param['nb_neurons'] * param['resolution'] ) # for the mean firing rate in in KHZ

        level_log = param['level_log']
        self.logger = logging.getLogger('analyse')
        fh = logging.FileHandler(path+'/nest_to_tvb_science.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        if level_log == 0:
            fh.setLevel(logging.DEBUG)
            self.logger.setLevel(logging.DEBUG)
        elif  level_log == 1:
            fh.setLevel(logging.INFO)
            self.logger.setLevel(logging.INFO)
        elif  level_log == 2:
            fh.setLevel(logging.WARNING)
            self.logger.setLevel(logging.WARNING)
        elif  level_log == 3:
            fh.setLevel(logging.ERROR)
            self.logger.setLevel(logging.ERROR)
        elif  level_log == 4:
            fh.setLevel(logging.CRITICAL)
            self.logger.setLevel(logging.CRITICAL)

    def analyse(self,count,hist):
        """
        analyse the histogram to generate state variable and the time
        :param count: the number of step of synchronization
        :param hist: the data
        :return:
        """
        hist_slide = np.concatenate((self.buffer,np.squeeze(hist,1)))
        data = slidding_window(hist_slide,self.width)
        self.buffer = np.squeeze(hist_slide[-self.width:])
        times = np.array([count*self.synch,(count+1)*self.synch], dtype='d')
        self.logger.info(np.mean(data*self.coeff))
        return times,data*self.coeff