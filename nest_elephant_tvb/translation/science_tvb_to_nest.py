#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

import numpy as np
from nest_elephant_tvb.translation.rate_spike import rates_to_spikes
from quantities import ms,Hz
import logging

# Can be changed to the function we had with elephant, this is just a toy function
def toy_rates_to_spikes(rates,t_start,t_stop):
    '''
    transform rate in spike with random value for testing
    :param rates: rates from tvb
    :param t_start: time of starting simulation
    :param t_stop: time of ending simulation
    :return: times of spikes
    '''
    times = t_start + np.random.rand(rates.shape[-1]) * (t_stop-t_start)
    times = np.around(np.sort(np.array(times)), decimals=1)
    return times

class generate_data:
    def __init__(self,path,nb_spike_generator,param,function_select=2):
        """
        generate spike train for each neurons
        :param path : path for the logger files
        :param nb_spike_generator: number of spike generator/neurons in each regions
        """
        self.percentage_shared = param['percentage_shared'] # percentage of shared rate between neurons
        self.nb_spike_generator = nb_spike_generator        # number of spike generator
        self.nb_synapse = param['nb_synapses']
        self.function_translation = function_select #TODO add a parameter for this

        np.random.seed(param['seed'])

        # configure the logger
        level_log = param['level_log']
        self.logger = logging.getLogger('generator')
        fh = logging.FileHandler(path+'/tvb_to_nest_science.log')
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
            # Compute the rate to spike trains
            rate *= self.nb_synapse # rate of poisson generator ( due property of poisson process)
            rate += 1e-12 # avoid rate equals to zeros
            spike_shared = \
                rates_to_spikes(rate * self.percentage_shared * Hz,
                                time_step[0] * ms, time_step[1] * ms, variation=True)[0]
            spike_generate = np.empty(self.nb_spike_generator, dtype=np.object)
            for i in range(self.nb_spike_generator):
                spikes = \
                    rates_to_spikes(rate * (1 - self.percentage_shared) * Hz, time_step[0] * ms, time_step[1] * ms,
                                    variation=True)[0]
                spike_generate[i] = np.around(np.sort(np.concatenate((spikes, spike_shared))), decimals=1)
            self.logger.info('rate :'+str(rate)+' spikes :'+str(np.concatenate(spike_generate).shape))
            return spike_generate
        elif self.function_translation == 2:
            rate *= self.nb_synapse / self.percentage_shared # rate of poisson generator ( due property of poisson process)
            rate += 1e-12  # avoid rate equals to zeros
            spike_shared = np.round(rates_to_spikes(rate * Hz, time_step[0] * ms, time_step[1] * ms, variation=True)[0],1)
            select = np.random.binomial(n=1,p=self.percentage_shared,size=(self.nb_spike_generator,spike_shared.shape[0]))
            result = []
            for i in np.repeat([spike_shared],self.nb_spike_generator,axis=0)*select :
                result.append(i[np.where(i!=0)])
            return result






