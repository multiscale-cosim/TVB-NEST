#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

class CommunicationInternAbstract:
    """
    Abstract class for internal communication
    Limitation of spike and rate exchange
    """

    def __init__(self, logger=None, timer=None):
        """
        Initialisation of the communication intern
        here: definition of the logger
        :param logger: logger for the internal communication
        """
        if logger is None:
            raise Exception('Internal Communication : missing logger for the internal communication')
        self.logger = logger
        self.timer = timer

    def finalise(self):
        """
        Procedure before finalise MPI
        :return boolean : true if MPI finalise need to be call
        """
        raise Exception("Not implemented")

    # Section 1 : spike trains exchange
    databuffer = None  # shared buffer for spike exchange
    # shape of the data inside the buffer
    # 2 types of shape : 1) array with 1 number for continuous data
    #                    2) arrays with multiple number for a sequence of data
    shape_buffer = None
    send_spike_exit = False  # boolean to identify the end of the simulation

    # 1.1) Send spikes trains : OPTION 1: 2 functions before and send after to use databuffer
    def send_spikes_ready(self):
        """
        wait until it's ready to use the buffer
        """
        raise Exception("Not implemented")

    def send_spikes(self):
        """
        send the data inside the buffer to the receiver
        databuffer is the buffer to send
        shape_buffer need to be set at the good values
        """
        raise Exception("Not implemented")

    # 1.1) Send spikes trains : OPTION 2: 1 function to write data in buffer and send it
    def send_spikes_trains(self, spike_trains):
        """
        Write spike trains in buffer and send them
        :param spike_trains: array of spikes trains
        """
        raise Exception("Not implemented")

    # 1.2) Close connection with receiver
    def send_spikes_end(self):
        """
        close internal connection for sending spikes
        """
        raise Exception("Not implemented")

    # 2.1) Get spikes : Option 1 : 1 function to get spikes
    def get_spikes(self):
        """
        wait the sender to be ready and receive the spikes trains
        update also the shape of the data
        :return: spike trains
        """
        raise Exception("Not implemented")

    # 2.1) Get spikes : Option 2 : 1 function to get spikes
    def get_spikes_ready(self):
        """
        wait until the buffer and the shape are ready to be used
        """
        raise Exception("Not implemented")

    # 2.2) End Getting spikes
    # Mandatory to used after call the previous function
    def get_spikes_release(self):
        """
        end the receiving of the spikes
        """
        raise Exception("Not implemented")

    # 2.3) Close connection with the sender spikes
    def get_spikes_end(self):
        """
        close internal connection for getting spikes
        """
        raise Exception("Not implemented")

    # Section 2 : rate and time exchange
    get_time_rate_exit = False  # boolean to identify the end from getting function
    send_time_rate_exit = False  # boolean to identify the end from sending function

    # 1.1) Function to get time and rate
    def get_time_rate(self):
        """
        wait that the data are available and return them when it's ready
        :return: times and rates
        """
        raise Exception("Not implemented")

    # 1.2) Function to send the end receiving rate and time
    # Mandatory to used after call the previous function
    def get_time_rate_release(self):
        """
        end the read of the data
        """
        raise Exception("Not implemented")

    # 1.3) Close getting time and rate
    def get_time_rate_end(self):
        """
        close the connection for receiving data
        """
        raise Exception("Not implemented")

    # 2.1) Send time and rate
    def send_time_rate(self, time_step, rate):
        """
        send time and rate
        :param time_step: time of simulation [begin,end]
        :param rate: rate to send
        """
        raise Exception("Not implemented")

    # 2.2) Close sending time and rate
    def send_time_rate_end(self):
        """
        close the connection for sending data
        """
        raise Exception("Not implemented")
