#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

# this file is based on the github repository : https://github.com/w-klijn/simplepytimer # TODO check the licence compatibility
import numpy as np
import time

class Timer():
    """
    This class is to provide a simple timer for record time during the execution of the program
    """
    def __init__(self,nb_slot,nb_times):
        """
        initialisation
        :param nb_slot: number of different timer
        :param nb_times: maximum of time recording
        """
        self._buffer = np.empty((nb_slot,nb_times*2)) # take the memory for avoid the increase of timer during the execution
        self._buffer[:] = np.NAN # file the buffer with non values
        self._index = np.zeros(nb_slot,dtype=int) # prepare the index for recording time

    def start(self,slot):
        """
        start timer ( record the time of start timer)
        :param slot: define the slot of the timer
        """
        self._buffer[slot,self._index[slot]] = time.time()

    def stop(self,slot):
        """
        stop timer ( record the timer of stopping the timer)
        increase the index for record the next time
        :param slot: define the slot of the timer
        """
        self._buffer[slot,self._index[slot]+1] = time.time()
        self._index[slot] += 2

    def change(self,slot_1,slot_2):
        """
        changing timer between to slot
        :param slot_1: slot of the first one
        :param slot_2: slot of the second one
        :return:
        """
        self.stop(slot_1)
        self.start(slot_2)

    def save(self, path):
        """
        save the buffer in a file
        :param path:
        :return:
        """
        np.save(path,self._buffer)


if __name__ == "__main__":
    """ test the timer """
    timer = Timer(4,10)
    ###############################################################
    timer.start(0)
    time.sleep(0.1)
    timer.start(1)
    time.sleep(0.1)
    timer.stop(0)
    timer.stop(1)

    timer.start(1)
    time.sleep(0.1)
    timer.change(1,0)
    time.sleep(0.1)
    timer.start(3)
    time.sleep(0.1)
    timer.stop(3)
    timer.stop(0)

    # This could also be in a loop!
    for idx in range(0,10):
        timer.start(2)
        time.sleep(0.1)
        timer.stop(2)

    timer.save('./save.npy')

