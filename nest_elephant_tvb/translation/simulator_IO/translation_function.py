#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import os
import numpy as np
from quantities import ms, Hz
from nest_elephant_tvb.translation.communication.mpi_io_external import MPICommunicationExtern
from nest_elephant_tvb.translation.translation_function.rate_spike import rates_to_spikes, slidding_window


class TranslationSpikeRate(MPICommunicationExtern):
    """
    Class for the translation between spike to rate
    """
    def __init__(self, id_translator, param, *arg, **karg):
        """
        translation object from spikes to rate
        :param id_translator : id of the translator
        :param param: parameter of the translation function
        :param arg: parameters
        :param karg: other parameters
        """
        super().__init__(*arg, **karg)
        self.id = id_translator
        self.synch = param['synch']                # time of synchronization between 2 run
        self.dt = param['resolution']              # the resolution of the integrator
        self.path_init = param['init']              # path of numpy array which are use to initialise the communication
        self.shape = (int(self.synch/self.dt), 1)  # the shape of the buffer/histogram
        self.width = int(param['width']/param['resolution'])  # the window of the average in time
        self.buffer = np.zeros((self.width,))                 # initialisation/ previous result for a good result
        # multiplicative coefficient : change the counting of spike in mean firing rate (KHZ)
        self.coeff = 1 / (param['nb_neurons'] * self.dt)
        # variable for saving values:
        self.save_hist = bool(param['save_hist'])
        if self.save_hist:
            self.save_hist_buf = None
            self.save_hist_path = arg[1] + '/translation/TSR_hist/'  # arg[1]: path of simulation + need path management
            self.save_hist_count = param['save_hist_count']
            self.save_hist_nb = 0
        self.save_rate = bool(param['save_rate'])
        if self.save_rate:
            self.save_rate_buf = None
            self.save_rate_path = arg[1] + '/translation/TSR_rate/'  # arg[1]: path of simulation + need path management
            self.save_rate_count = param['save_rate_count']
            self.save_rate_nb = 0

    def simulation_time(self):
        """
        Translation function of the spike to rate :
            1) get the spike
            2) transform spike to rate
            3) send rate
        The step 1 and 3 need to be dissociate for synchronization requirement.
        This dissociation allow the translation module to buffer one more step from the sender or the receiver.
        This function is very important for the speed of the simulation
        """
        # initialisation of the communication
        self.logger.info('TRS : begin sim')
        rates = np.load(self.path_init)
        self.logger.info('TRS : init rates')
        self.communication_internal.send_time_rate(np.array([0.,self.synch]), rates)  # The time is not good because the TVB interface has a bug
        self.logger.info('TRS : send init')
        count = 0  # counter of the number of run. It can be useful for the translation function
        while True:
            # Step 1: INTERNAL : get spike
            self.logger.info('TSR : receive data Nest')
            self.communication_internal.get_spikes_ready()
            if self.communication_internal.shape_buffer[0] == -1:
                self.logger.info('TSR : break')
                break

            # Step 2.1: take all data from buffer and create histogram
            self.logger.info('TSR : add spikes '+str(self.communication_internal.shape_buffer[0]))
            hist = self.add_spikes(count,
                                   self.communication_internal.shape_buffer[0],
                                   self.communication_internal.databuffer)

            # Step 2.2 : INTERNAL: end get spike (important to be here for optimization/synchronization propose)
            self.communication_internal.get_spikes_release()
            # optional save the histogram
            if self.save_hist:
                if count % self.save_hist_count == 0:
                    if self.save_hist_buf is not None:
                        self.logger.info('TSR : save hist :' + str(self.save_rate_nb))
                        np.save(self.save_hist_path+'/'+str(self.id)+'_'+str(self.save_hist_nb)+'.npy', self.save_hist_buf)
                        self.save_hist_nb += 1
                    self.save_hist_buf = hist
                else:
                    self.save_hist_buf = np.concatenate((self.save_hist_buf, hist))

            # Step 2.3: Analyse this data, i.e. calculate mean firing rate
            self.logger.info('TSR : analise')
            times, rate = self.analyse(count+1, hist)  # if fix bug of initilisation remove +1
            # optional : save rate
            if self.save_rate:
                if count % self.save_rate_count == 0:
                    self.logger.info('TSR : save rate :'+str(self.save_rate_nb))
                    if self.save_rate_buf is not None:
                        np.save(self.save_rate_path+'/'+str(self.id)+'_'+str(self.save_rate_nb)+'.npy', self.save_rate_buf)
                        self.save_rate_nb += 1
                    self.save_rate_buf = rate
                else:
                    self.save_rate_buf = np.concatenate((self.save_rate_buf, rate))

            # Step 3: INTERNAL: send rate and time
            self.logger.info('TSR : send data')
            self.communication_internal.send_time_rate(times, rate)
            if self.communication_internal.send_time_rate_exit:
                self.logger.info('TSR : break 2')
                break

            # Step 4 : end loop
            count += 1
        # INTERNAL: Close all the internal communication
        self.logger.info('TSR : end methods')
        self.communication_internal.get_spikes_end()
        self.communication_internal.send_time_rate_end()
        self.logger.info('TSR : end')

    def finalise(self):
        super().finalise()
        # Save the ending part of the simulation
        if self.save_hist:
            np.save(self.save_hist_path + '/' + str(self.id) + '_' + str(self.save_hist_count) + '.npy', self.save_hist_buf)
        if self.save_rate:
            np.save(self.save_rate_path + '/' + str(self.id) + '_' + str(self.save_rate_nb) + '.npy', self.save_rate_buf)

    def add_spikes(self, count, size_buffer, buffer):
        """
        adding spike in the histogram
        :param count: the number of synchronization times
        :param size_buffer: the total number of data in the buffer
        :param buffer: buffer which contains data
        """
        hist = np.zeros(self.shape)
        self.logger.info('TSR : add_spikes : size buffer : '+str(size_buffer))
        if size_buffer != 0:
            if size_buffer % 3 != 0:  # the data is compose of a series of 3 elements (id_detector,id_neurons,times)
                raise Exception('TRS : add spike : bad shape of the input '+str(size_buffer))
            # get all the time of the spike and add them in a histogram
            for index_data in range(int(np.rint(size_buffer/3))):
                index_hist = int(np.rint((buffer[index_data*3+2]-count*self.synch)/self.dt))-1
                if index_hist >= hist.shape[0] or index_hist < 0:
                    self.logger.info('ERROR :TSR : add_spikes : buffer :'+str(buffer[:size_buffer]))
                    self.logger.info('ERROR : TSR : add_spikes : data :'+str(hist.shape[0])+' '+str(index_data*3+2)+' '+str(buffer[index_data*3+2])+' '+str(count*self.synch)+' '+str(self.synch)+' '+str(index_hist))
                    self.logger.info('ERROR : TSR : add_spikes : cond 1 : '+str(index_hist >= hist.shape[0] )+'cond 2 :'+str(index_hist < 0))
                    raise Exception("TSR : add spike: The input data can't be add to the histogram")
                hist[index_hist] += 1
        return hist

    def analyse(self, count, hist):
        """
        analyse the histogram to generate state variable and the time
        :param count: the number of step of synchronization
        :param hist: the data
        :return:
        """
        hist_slide = np.concatenate((self.buffer, np.squeeze(hist, 1)))
        data = slidding_window(hist_slide, self.width)
        self.buffer = np.squeeze(hist_slide[-self.width:])
        times = np.array([count*self.synch, (count+1)*self.synch], dtype='d')
        self.logger.info('TSR : analyse : '+str(np.mean(data*self.coeff)))
        return times, data*self.coeff


class TranslationRateSpike(MPICommunicationExtern):
    """
    Class for the translation between rate to spike
    """
    def __init__(self, id_translator, param, nb_spike_generator, *arg, **karg):
        """
        translation from rate to spike trains
        :param param: parameter for the translation function
        :param nb_spike_generator: number of spike generator
        :param arg: parameters
        :param karg: other parameters
        """
        super().__init__(*arg, **karg)
        self.id = id_translator
        self.percentage_shared = param['percentage_shared']   # percentage of shared rate between neurons
        self.nb_spike_generator = nb_spike_generator          # number of spike generator
        self.nb_synapse = param['nb_synapses']                # number of synapses by neurons
        self.function_translation = param['function_select']  # choose the function for the translation
        # self.path_init = param['init']              # path of numpy array which are use to initialise the communication
        np.random.seed(param['seed'])               # set the seed for repeatability
        # variable for saving values:
        self.save_spike = bool(param['save_spike'])
        if self.save_spike:
            self.save_spike_buf = None
            self.save_spike_path = arg[1] + '/translation/TRS_spike/'  # arg[0]: path of simulation+need path management
            self.save_spike_count = param['save_spike_count']
            self.save_spike_nb = 0
        self.save_rate = bool(param['save_rate'])
        if self.save_rate:
            self.save_rate_buf = None
            self.save_rate_path = arg[1] + '/translation/TRS_rate/'  # arg[0]: path of simulation + need path management
            self.save_rate_count = param['save_rate_count']
            self.save_rate_nb = 0
        self.logger.info('TRS : end init translation')

    def simulation_time(self):
        """
        Translation function of the rate to spike :
            1) get the rate
            2) transform rate to spike
            3) send spike trains
        The step 1 and 3 need to be dissociate for synchronization requirement.
        This dissociation allow the translation module to buffer one more step from the sender or the receiver.
        This function is very important for the speed of the simulation.
        """
        # initialisation of the communication # TVB already did it
        # self.logger.info('TRS : begin sim')
        # spike_trains = np.load(self.path_init)
        # self.logger.info('TRS : init spike trains')
        # self.communication_internal.send_spikes_trains(spike_trains)
        # self.logger.info('TRS : send init')
        count = 0  # counter of the number of run. It use to send the good time to TVB
        while True:
            # Step 1.1: INTERNAL : get rate
            self.logger.info('TRS : get rate')
            times, rate = self.communication_internal.get_time_rate()
            if self.communication_internal.get_time_rate_exit:
                self.logger.info('TRS : break end sender')
                break
            # Step 1.2: INTERNAL : end getting rate (important to be here for optimization/synchronization propose)
            self.communication_internal.get_time_rate_release()
            # optional :  save the rate
            if self.save_rate:
                if count % self.save_rate_count == 0:
                    if self.save_rate_buf is not None:
                        np.save(self.save_rate_path + '/' + str(self.id) + '_' + str(self.save_rate_nb) + '.npy', self.save_rate_buf)
                        self.save_rate_nb += 1
                    self.save_rate_buf = rate
                else:
                    self.save_rate_buf = np.concatenate((self.save_rate_buf, rate))

            # Step 2: generate spike trains
            # improvement : we can generate other type of data but Nest communication need to be adapted for it
            self.logger.info('TRS : generate spike')
            spike_trains = self.generate_spike(count, times, rate)
            if self.save_spike:
                if count % self.save_spike_count == 0:
                    if self.save_spike_buf is not None:
                        np.save(self.save_spike_path + '/' + str(self.id) + '_' + str(self.save_spike_nb) + '.npy', self.save_spike_buf)
                        self.save_spike_nb += 1
                    self.save_spike_buf = [spikes for spikes in spike_trains]
                else:
                    tmp = []
                    for index, spikes in enumerate(spike_trains):
                        tmp.append(np.concatenate((self.save_spike_buf[index], spikes)))
                    self.save_spike_buf = tmp

            # Step 3: send spike trains to Nest
            self.logger.info('TRS : send spike train')
            self.communication_internal.send_spikes_trains(spike_trains)
            if self.communication_internal.send_spike_exit:
                self.logger.info('TRS : break')
                break

            # Step 4 : end loop
            count += 1
        # INTERNAL: Close all the internal communication
        self.logger.info('TRS : end method by TVB : '+str(self.communication_internal.get_time_rate_exit))
        self.communication_internal.get_time_rate_end()
        self.communication_internal.send_spikes_end()
        self.logger.info('TRS : end')

    def finalise(self):
        super().finalise()
        # Save the ending part of the simulation
        if self.save_rate:
            np.save(self.save_rate_path + '/' + str(self.id) + '_' + str(self.save_rate_nb) + '.npy', self.save_rate_buf)
        if self.save_spike:
            np.save(self.save_spike_path + '/' + str(self.id) + '_' + str(self.save_spike_nb) + '.npy', self.save_spike_buf)

    def generate_spike(self, count, time_step, rate):
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
            rate *= self.nb_synapse  # rate of poisson generator ( due property of poisson process)
            rate += 1e-12  # avoid rate equals to zeros
            # generate the shared spikes
            spike_shared = \
                rates_to_spikes(rate * self.percentage_shared * Hz,
                                time_step[0] * ms, time_step[1] * ms, variation=True)[0]
            # generate individual spike trains
            spike_generate = rates_to_spikes(np.repeat([rate], self.nb_spike_generator, axis=0)
                                             * (1 - self.percentage_shared) * Hz,
                                             time_step[0] * ms, time_step[1] * ms,
                                             variation=True)
            # create all individual spike trains by concatenation of the individual ans shared spike trains
            for i in range(self.nb_spike_generator):
                spike_generate[i] = np.around(np.sort(np.concatenate((spike_generate, spike_shared))), decimals=1)
            self.logger.info('TRS : rate :'+str(rate)+' spikes :'+str(np.concatenate(spike_generate).shape))
            return spike_generate

        elif self.function_translation == 2:
            # Multiple Interaction Process Model
            # rate of poisson generator (due property of poisson process)
            rate *= self.nb_synapse / self.percentage_shared
            rate += 1e-12  # avoid rate equals to zeros
            # generate the reference spike trains
            spike_ref = np.round(rates_to_spikes(rate * Hz, time_step[0] * ms, time_step[1] * ms,
                                                 variation=True)[0], 1)
            # generate the selection of spikes for each neurons
            select = np.random.binomial(n=1, p=self.percentage_shared,
                                        size=(self.nb_spike_generator, spike_ref.shape[0]))
            # create individual spike trains
            result = []
            for i in np.repeat([spike_ref], self.nb_spike_generator, axis=0)*select:
                result.append(i[np.where(i != 0)])
            self.logger.info('TRS : rate :'+str(np.sum(rate))+' spikes :'+str(spike_ref.shape[0]))
            return result
