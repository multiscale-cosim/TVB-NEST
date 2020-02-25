import numpy as np
import copy

def slidding_window(data,width):
    """
    use for mean field
    :param data: instentaneous firing rate
    :param width: windows or times average of the mean field
    :return: state variable of the mean field
    """
    res = np.zeros((data.shape[0]-width,width))
    res [:,:] = data[[[ i+j for i in range(width) ] for j in range(data.shape[0]-width)]]
    return res.mean(axis=1)

class store_data:
    def __init__(self,shape,synch,dt):
        """
        initialisation
        :param shape: shape of the histogram
        :param synch: time of synchronization between simulator
        :param dt: integrator step of the tvb
        """
        self.hist = np.zeros(shape)
        self.shape = shape
        self.synch=synch
        self.dt=dt

    def add_spikes(self,count,data):
        """
        adding spike in the histogram
        :param count: the number of synchronization times
        :param data: the spike :(id,time)
        """
        data[1]-=self.dt
        self.hist[int((data[1]-count*self.synch)/self.dt)]+=1

    def return_data(self):
        """
        return the histogram and reinitialise the hsitogram
        :return: histogram
        """
        hist_copy = copy.copy(self.hist)
        self.hist = np.zeros(self.shape) # initialise histogram histogram of one region
        return hist_copy

class analyse_data:
    def __init__(self,width,synch):
        """
        initialisation
        :param width: the window of the average in time
        :param synch: synchronize time between simulator
        """
        self.init=np.zeros((width,)) #initialisation/ previous result for a good result
        self.width = width
        self.synch = synch

    def analyse(self,count,hist):
        """
        analyse the histogram to generate state variable and the time
        :param count: the number of step of synchronization
        :param buffer: the data
        :return:
        """
        hist_slide = np.concatenate((self.init,np.squeeze(hist,1)))
        data = slidding_window(hist_slide,self.width)
        self.init = np.squeeze(hist_slide[-self.width:])
        times = np.array([count*self.synch,(count+1)*self.synch], dtype='d')
        return times,data