from nest_elephant_tvb.translation.communication.mpi_io_external import MPI_communication_extern
import numpy as np
from nest_elephant_tvb.translation.rate_spike import rates_to_spikes
from quantities import ms,Hz

def slidding_window(data,width):
    """
    use for mean field
    :param data: instantaneous firing rate
    :param width: windows or times average of the mean field
    :return: state variable of the mean field
    """
    res = np.zeros((data.shape[0]-width,width))
    res [:,:] = np.squeeze(data[np.array([[ i+j for i in range(width) ] for j in range(data.shape[0]-width)])])
    return res.mean(axis=1)


class Translation_spike_to_rate(MPI_communication_extern):
    def __init__(self,param,*arg,**karg):
        super().__init__(*arg,**karg)
        self.synch=param['synch']                # time of synchronization between 2 run
        self.dt=param['resolution']              # the resolution of the integrator
        self.shape = (int(self.synch/self.dt),1) # the shape of the buffer/histogram
        self.width = int(param['width']/param['resolution']) # the window of the average in time
        self.buffer = np.zeros((self.width,))                  #initialisation/ previous result for a good result
        self.coeff = 1 / ( param['nb_neurons'] * self.dt ) # for the mean firing rate in in KHZ

    # See todo in the beginning, encapsulate I/O, transformer, science parts
    def simulation_time(self):
        '''
        All analysis and science stuff in one place.
        Done in three steps, that were previously disconnected.
        Step 1 and 2 were done in the receiving thread, step 3 in the sending thread.
        NOTE: All science and analysis is the same as before.
        :param count: Simulation iteration/step
        :param databuffer: The buffer contains the spikes of the current step
        :param store: Python object, create the histogram
        :param analyse: Python object, calculate rates
        :return times, data: simulation times and the calculated rates

        TODO: Step 1 and 2 can be merged into one step. Buffer is no longer filled rank by rank.
        TODO: Make this parallel with the INTRA communicator (should be embarrassingly parallel).
        '''
        count = 0
        while True:
            self.communication_internal.get_spikes_ready()
            self.logger.info('TSR : request TVB : ' + str(self.communication_internal.shape_buffer))
            if self.communication_internal.shape_buffer[0] == -1:
                self.logger.info('TSR : break')
                break

            # Step 1) take all data from buffer and create histogram
            # second to last index in databuffer denotes how much data there is
            self.logger.info('TSR : add spikes '+str(self.communication_internal.shape_buffer[0]))
            hist = self.add_spikes(count,self.communication_internal.shape_buffer[0],self.communication_internal.databuffer)
            self.communication_internal.get_spikes_release()

            # Step 2) Analyse this data, i.e. calculate rates?
            self.logger.info('TSR : analise')
            times,rate = self.analyse(count,hist)

            self.logger.info('TSR : send data')
            self.communication_internal.send_time_rate(times,rate)
            self.logger.info('TSR : ready ? ' + str(self.communication_internal.send_time_rate_exit))
            if self.communication_internal.send_time_rate_exit:
                self.logger.info('TSR : break 2')
                break
            count += 1
        self.logger.info('TSR : end methods')
        self.communication_internal.get_spikes_end()
        self.communication_internal.send_time_rate_end()
        self.logger.info('TSR : end')


    def add_spikes(self,count,size_buffer,buffer):
        """
        adding spike in the histogram
        :param count: the number of synchronization times
        :param datas: the spike :(id,time)
        """
        hist = np.zeros(self.shape)
        self.logger.info('TSR : add_spikes : size buffer : '+str(size_buffer))
        if size_buffer != 0:
            if size_buffer%3 !=0:
                self.logger.info('TSR : add_spikes : bad shape of data '+str(size_buffer))
                raise Exception('bad shape of the input ')
            for index_data in range(int(np.rint(size_buffer/3))):
                index_hist = int(np.rint((buffer[index_data*3+2]-count*self.synch)/self.dt))-1
                if index_hist>=hist.shape[0] or index_hist <0:
                    self.logger.info('TSR : add_spikes : buffer :'+str(buffer[:size_buffer]))
                    self.logger.info('TSR : add_spikes : data :'+str(hist.shape[0])+' '+str(index_data*3+2)+' '+str(buffer[index_data*3+2])+' '+str(count*self.synch)+' '+str(self.synch )+' '+str(index_hist))
                hist[index_hist]+=1
                #self.logger.info(index_data*3+2)
        return hist

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
        self.logger.info('TSR : analyse : '+ str(np.mean(data*self.coeff)))
        return times,data*self.coeff


class Translation_rate_to_spike(MPI_communication_extern):
    def __init__(self,param,nb_spike_generator,*arg,**karg):
        super().__init__(*arg,**karg)
        self.percentage_shared = param['percentage_shared']  # percentage of shared rate between neurons
        self.nb_spike_generator = nb_spike_generator         # number of spike generator
        self.nb_synapse = param['nb_synapses']               # number of synapses by neurons
        self.function_translation = param['function_select'] # choose the function for the translation
        np.random.seed(param['seed'])
        self.path_init =param['init']
        self.req_send = None
        self.logger.info('TRS : end init translation')


    def simulation_time(self):
        self.logger.info('TRS : begin sim')
        spike_trains = np.load(self.path_init)
        self.logger.info('TRS : init spike trains')
        self.communication_internal.send_spikes_trains(spike_trains)
        self.logger.info('TRS : send init')
        while True:
            self.logger.info('TRS : star loop')
            times,rate = self.communication_internal.get_time_rate()
            if self.communication_internal.get_time_rate_exit:
                self.logger.info('TRS : break end sender')
                break
            self.communication_internal.get_time_rate_release()
            self.logger.info('TRS : generate spike')
            spike_trains = self.generate_spike(0,times,rate)
            self.logger.info('TRS : send spike train')
            self.communication_internal.send_spikes_trains(spike_trains)
            if self.communication_internal.send_spike_exit:
                self.logger.info('TRS : break')
                break
        self.logger.info('TRS : end method by TVB : '+str(self.communication_internal.get_time_rate_exit))
        self.communication_internal.get_time_rate_end()
        self.communication_internal.send_spikes_end()
        self.logger.info('TRS : end')

    def generate_spike(self,count,time_step,rate):
        """
        generate spike
        This function are based on the paper : Kuhn, Alexandre, Ad Aertsen, and Stefan Rotter. “Higher-Order Statistics of Input Ensembles and the Response of Simple Model Neurons.” Neural Computation 15, no. 1 (January 2003): 67–101. https://doi.org/10.1162/089976603321043702.
        DOI: 10.1162/089976603321043702
        function 1 : Single Interaction Process Model
        function 2 : Multiple Interaction Process Model
        :param count: the number of step of synchronization between simulators
        :param time_step: the time of synchronization
        :param rate: the input rate of the mean field
        :return:
        """
        if self.function_translation == 1:
            # Single Interaction Process Model
            # Compute the rate to spike trains
            rate *= self.nb_synapse # rate of poisson generator ( due property of poisson process)
            rate += 1e-12 # avoid rate equals to zeros
            spike_shared = \
                rates_to_spikes(rate * self.percentage_shared * Hz,
                                time_step[0] * ms, time_step[1] * ms, variation=True)[0]
            spike_generate = rates_to_spikes(np.repeat([rate],self.nb_spike_generator,axis=0) * (1 - self.percentage_shared) * Hz, time_step[0] * ms, time_step[1] * ms,
                                    variation=True)
            for i in range(self.nb_spike_generator):
                spike_generate[i] = np.around(np.sort(np.concatenate((spike_generate, spike_shared))), decimals=1)
            self.logger.info('TRS : rate :'+str(rate)+' spikes :'+str(np.concatenate(spike_generate).shape))
            return spike_generate
        elif self.function_translation == 2:
            # Multiple Interaction Process Model
            rate *= self.nb_synapse / self.percentage_shared # rate of poisson generator ( due property of poisson process)
            rate += 1e-12  # avoid rate equals to zeros
            spike_shared = np.round(rates_to_spikes(rate * Hz, time_step[0] * ms, time_step[1] * ms, variation=True)[0],1)
            select = np.random.binomial(n=1,p=self.percentage_shared,size=(self.nb_spike_generator,spike_shared.shape[0]))
            result = []
            for i in np.repeat([spike_shared],self.nb_spike_generator,axis=0)*select :
                result.append(i[np.where(i!=0)])
            # self.logger.info('TRS : rate :'+str(rate)+' spikes :'+str(spike_shared))
            return result
