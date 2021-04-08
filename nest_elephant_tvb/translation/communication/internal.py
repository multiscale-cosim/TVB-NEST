
class CommunicationInternAbstract():
    def __init__(self,logger=None):
        if logger is None:
            raise Exception('missing logger for the internal communication')
        self.logger = logger

    def finalise(self):
        raise Exception("Not implemented")

    databuffer = None
    shape_buffer = None
    send_spike_exit = False
    def send_spikes_ready(self):
        raise Exception("Not implemented")

    def send_spikes(self):
        raise Exception("Not implemented")

    def send_spikes_trains(self,spike_trains):
        raise Exception("Not implemented")

    def send_spikes_end(self):
        raise Exception("Not implemented")

    def get_spikes(self):
        raise Exception("Not implemented")

    def get_spikes_ready(self):
        raise Exception("Not implemented")

    def get_spikes_release(self):
        raise Exception("Not implemented")

    def get_spikes_end(self):
        raise Exception("Not implemented")

    get_time_rate_exit = False
    send_time_rate_exit = False
    def get_time_rate(self):
        raise Exception("Not implemented")

    def get_time_rate_release(self):
        raise Exception("Not implemented")

    def get_time_rate_end(self):
        raise Exception("Not implemented")

    def send_time_rate(self, time_step, rate):
        raise Exception("Not implemented")

    def send_time_rate_end(self):
        raise Exception("Not implemented")
