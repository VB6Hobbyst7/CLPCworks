# -*- coding: utf-8 -*-
"""
Created on Sun Dec  6 16:11:32 2020

@author: zhangxi
"""

import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        start_time = time.time()
        func(*args,**kwargs)
        end_time = time.time()
        print('函数%s运行时间为：%.2fs' % (func.__name__,end_time - start_time))
    return wrapper