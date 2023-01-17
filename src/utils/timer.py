""" Util functions for timer related purposes """

import inspect
import threading


def set_interval(func, sec):
    """ Executes given function periodically, every given seconds """
    def func_wrapper():
        print('Executing scheduled function', inspect.getsource(func))
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t
