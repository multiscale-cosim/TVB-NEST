from elephant.spike_train_generation import homogeneous_poisson_process, inhomogeneous_poisson_process
from elephant.statistics import mean_firing_rate
import numpy as np
from neo import AnalogSignal
from quantities import Hz

def rates_to_spikes( rates,t_start,t_stop, variation=False):
    """
    Generate spike train with homogenous or inhomogenous Poisson generator
    :param rates: an array or a float of quantities
    :param t_start: time to start spike train
    :param t_stop: time where the spike train stop
    :param variation: Boolean for variation of rate
    :return: one or multiple spike train
    """
    if variation:
        # the case where the variation of the rate is include
        # We generate the inhomogenous poisson
        if len(rates.shape) == 1:
            # the case where we have only one rate
            signal = AnalogSignal(rates, t_start=t_start, sampling_period=(t_stop-t_start)/rates.shape[-1])
            result = [inhomogeneous_poisson_process(signal,as_array=True)]
            return np.array(result)
        else :
            # the case where we have multiple rates
            result = []
            for rate in rates:
                signal = AnalogSignal(rate, t_start=t_start, sampling_period=(t_stop - t_start) / rates.shape[-1])
                result.append(inhomogeneous_poisson_process(signal,as_array=True))
            return np.array(result)
    else:
        # the case we have only the rate
        # We generate the homogenous poisson
        if len(rates.shape) ==0:
            # the case where we have only one rate
            result = np.array([homogeneous_poisson_process(rate=rates, t_start=t_start, t_stop=t_stop, as_array=True)])
        else:
            # the case where we have multiple rates
            result = []
            for rate in rates:
                result.append(homogeneous_poisson_process(rate=rate, t_start=t_start, t_stop=t_stop, as_array=True))
        return np.array(result)

def spikes_to_rate( spikes,t_start,t_stop, windows=0.0):
    """
    Compute the rate of one spike train or multiple of spike trains

    #TODO : need to have add the overlapping of windows
    :param spikes: one spike train or multiple spike train
    :param t_start: time to start to compute rate
    :param t_stop: time to stop to compute rate
    :param windows: the window for compute rate
    # :param overlaps: FUTURE overlasp of window
    :return: rates or variation of rates
    """

    if windows == 0.0:
        #case without variation of rate
        if len(spikes[0].shape) ==0:
            # with only one rate
            result = [mean_firing_rate(spiketrain=spikes,t_start=t_start,t_stop=t_stop).rescale(Hz)]
        else:
            # with multiple rate
            result = []
            for spike in spikes:
                result.append(mean_firing_rate(spiketrain=spike,t_start=t_start,t_stop=t_stop).rescale(Hz))
        return np.array(result)
    else:
        # case with variation of rate
        rate = []
        for time in np.arange(t_start,t_stop,windows):
            t_start_window = time*t_start.units
            t_stop_window = t_start_window+windows
            if len(spikes[0].shape) == 0:
                # for only one spike train
                result = [mean_firing_rate(spiketrain=spikes, t_start=t_start_window, t_stop=t_stop_window).rescale(Hz)]
            else:
                # for multiple spike train
                result = []
                for spike in spikes:
                    result.append(mean_firing_rate(spiketrain=spike, t_start=t_start_window, t_stop=t_stop_window).rescale(Hz))
            rate.append(result)
        return np.array(rate)