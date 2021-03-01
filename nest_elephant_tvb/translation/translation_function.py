from nest_elephant_tvb.translation.mpi_translator import MPI_communication
from mpi4py import MPI
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


class Translation_spike_to_rate(MPI_communication):
    def __init__(self,param,receiver_rank,*arg,**karg):
        super().__init__(*arg,**karg)
        self.synch=param['synch']                # time of synchronization between 2 run
        self.dt=param['resolution']              # the resolution of the integrator
        self.shape = (int(self.synch/self.dt),1) # the shape of the buffer/histogram
        self.width = int(param['width']/param['resolution']) # the window of the average in time
        self.buffer = np.zeros((self.width,))                  #initialisation/ previous result for a good result
        self.coeff = 1 / ( param['nb_neurons'] * self.dt ) # for the mean firing rate in in KHZ
        self.receiver_rank = receiver_rank
        self.logger.info('end init translation')

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
        req_1 = None
        req_2 = None
        req_check = None
        ready = None
        while True:

            self.logger.info('loop start')
            size_buffer = self.ready_to_read()
            self.logger.info('ready to write : '+str(size_buffer))
            if size_buffer == -1:
                break

            # Step 1) take all data from buffer and create histogram
            # second to last index in databuffer denotes how much data there is
            hist = self.add_spikes(count,size_buffer)
            self.end_read()

            # Step 2) Analyse this data, i.e. calculate rates?
            times,data = self.analyse(count,hist)


            self.logger.info('request TVB : '+str(size_buffer))
            if req_1 is not None:
                req_1.wait()
                req_2.wait()
                ready = req_check.wait()
                if not ready:
                    self.logger.info('end : ' + str(ready))
                    break
            # time of stating and ending step
            req_1 = MPI.COMM_WORLD.isend(times, dest=self.receiver_rank, tag=0)
            # send the size of the rate
            req_2 = MPI.COMM_WORLD.isend(data, dest=self.receiver_rank, tag=1)
            req_check = MPI.COMM_WORLD.irecv(source=self.receiver_rank)
            count += 1

        self.release_read_buffer(size_buffer)
        if ready:
            req_1 = MPI.COMM_WORLD.isend([-1], dest=self.receiver_rank, tag=0)


    def add_spikes(self,count,size_buffer):
        """
        adding spike in the histogram
        :param count: the number of synchronization times
        :param datas: the spike :(id,time)
        """
        hist = np.zeros(self.shape)
        self.logger.info('size buffer : '+str(size_buffer))
        if size_buffer != 0:
            if size_buffer%3 !=0:
                self.logger.info('bad shape of data '+str(size_buffer))
            for index_data in range(int(np.rint(size_buffer/3))):
                index_hist = int(np.rint((self.databuffer[index_data*3+2]-count*self.synch)/self.dt))-1
                if index_hist>=hist.shape[0] or index_hist <0:
                    self.logger.info(self.databuffer[:size_buffer])
                    self.logger.info('data :'+str(hist.shape[0])+' '+str(index_data*3+2)+' '+str(self.databuffer[index_data*3+2])+' '+str(count*self.synch)+' '+str(self.synch )+' '+str(index_hist))
                hist[index_hist]+=1
                self.logger.info(index_data*3+2)
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
        self.logger.info(np.mean(data*self.coeff))
        return times,data*self.coeff


class Translation_rate_to_spike(MPI_communication):
    def __init__(self,param,sender_rank,nb_spike_generator,*arg,**karg):
        super().__init__(*arg,**karg)
        self.percentage_shared = param['percentage_shared']  # percentage of shared rate between neurons
        self.nb_spike_generator = nb_spike_generator         # number of spike generator
        self.nb_synapse = param['nb_synapses']               # number of synapses by neurons
        self.function_translation = param['function_select'] # choose the function for the translation

        np.random.seed(param['seed'])
        self.sender_rank = sender_rank
        self.path_init =param['init']

    def simulation_time(self):
        spike_trains = np.load(self.path_init)
        self.ready_write_buffer()
        self.logger.info('start spike_trains in buffer')
        data_shape = []
        for index, spike_train in enumerate(spike_trains):
            data_shape.append(len(spike_train))
            # self.logger.info("spike times : "+str(index)+" " +str(len(spike_train))+
            #                  "\n"+str(spike_train))
        self.logger.info(str(np.concatenate(spike_trains)))
        data = np.concatenate(spike_trains)
        self.logger.info(str(data.shape))
        self.size_buffer = data_shape
        self.databuffer[:data.shape[0]] = data
        self.end_writing()

        req_send = None
        while True:
            if req_send is not None:
                req_send.wait()
            req_time = MPI.COMM_WORLD.irecv(source=self.sender_rank,tag=0)
            req_data = MPI.COMM_WORLD.irecv(source=self.sender_rank,tag=1)
            time_step = req_time.wait()
            if time_step[0] == -1:
                self.logger.info('break end sender')
                break
            rate = req_data.wait()
            spike_trains = self.generate_spike(0,time_step,rate)

            self.ready_write_buffer()
            self.logger.info('start spike_trains in buffer')
            data_shape = []
            for index, spike_train in enumerate(spike_trains):
                data_shape.append(len(spike_train))
                # self.logger.info("spike times : "+str(index)+" " +str(len(spike_train))+
                #                  "\n"+str(spike_train))
            self.logger.info( str(np.concatenate(spike_trains)))
            data = np.concatenate(spike_trains)
            self.logger.info(str(data.shape))
            self.size_buffer=data_shape
            self.databuffer[:data.shape[0]] = data
            self.end_writing()

            req_send = MPI.COMM_WORLD.isend(True, dest=self.sender_rank)

        self.logger.info('end method by TVB : '+str(time_step[0]))
        if time_step[0] == -1:
            self.logger.info('end method by TVB')
            MPI.COMM_WORLD.isend(False, dest=self.sender_rank)
        self.release_write_buffer()



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
            self.logger.info('rate :'+str(rate)+' spikes :'+str(np.concatenate(spike_generate).shape))
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
            # self.logger.info('rate :'+str(rate)+' spikes :'+str(spike_shared))
            return result
