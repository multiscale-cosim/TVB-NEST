# this file is based on the github repository : https://github.com/w-klijn/simplepytimer
import numpy as np
import time

class Timer():
    def __init__(self,nb_slot,nb_times):
        self._buffer = np.empty((nb_slot,nb_times*2))
        self._buffer[:] = np.NAN
        self._index = np.zeros(nb_slot,dtype=int)

    def start(self,slot):
        self._buffer[slot,self._index[slot]] = time.time()

    def stop(self,slot):
        self._buffer[slot,self._index[slot]+1] = time.time()
        self._index[slot] += 2

    def change(self,slot_1,slot_2):
        self.stop(slot_1)
        self.start(slot_2)

    def save(self, path):
        np.save(path,self._buffer)

    # def print(self):


if __name__ == "__main__":
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

