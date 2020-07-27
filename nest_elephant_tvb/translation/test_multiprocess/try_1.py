from multiprocessing import Manager, Process, Lock, Value
import numpy as np
import time

size = 20
value_end = 10
def f(a,access,lock):
    for i in range(size):
        print('f ',len(a),a[0].shape)
        print('f : waiting access value')
        print(type(access), access.value)
        while access.value:
            pass
        print('f : modify a')
        print('f ',len(a),a[0].shape)
        array = a[0] # don't modify the array it self
        array[i] =value_end
        a[0] = array
        print('f : wait access change')
        with lock :
            access.value = True
        print('f : end')
    return

def g (a,access,lock):
    for i in range(size):
        print('g ',len(a),a[0].shape)
        print('g : wait access value')
        while not access.value:
            pass
        print('g : change a to big a')
        if i != 0:
            assert a[0][-1] == value_end
        a[0] = np.zeros((i+1,))
        print('g ',len(a),a[0].shape)
        print('g : wait access change')
        with lock:
            access.value = False
        print('g', type(access), access.value)
        print('g : end')
    return

if __name__ == '__main__':
    with Manager() as manager:
        l = manager.list([np.ones((10,))])
        value = Value('b', True)
        lock = Lock()

        p1 = Process(target=f, args=(l,value,lock))
        p2 = Process(target=g, args=(l,value,lock))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        print(l)
        print(l[0])
        print(len(l), l[0].shape)
