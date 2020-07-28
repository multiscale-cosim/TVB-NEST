import time
from multiprocessing import Process, Manager, Value

def foo(data, name=''):
    print(type(data), data.value, name)
    data.value += 1

if __name__ == "__main__":
        manager = Manager()
        x = manager.Value('i', 0)
        y = Value('i', 0)

        a = []
        for i in range(5):
            a.append(Process(target=foo, args=(x, 'x')))
            a.append(Process(target=foo, args=(y, 'y')))

        for p in a :
            p.start()

        print('Before waiting: ')
        print('x = {0}'.format(x.value))
        print('y = {0}'.format(y.value))

        for p in a :
            p.join()
        print('After waiting: ')
        print('x = {0}'.format(x.value))
        print('y = {0}'.format(y.value))