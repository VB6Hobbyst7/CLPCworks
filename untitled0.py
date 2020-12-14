# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 08:56:39 2020

@author: zhangxi
"""
import pandas as pd
import numpy as np
import os
import datetime
import time
import functools
import sys

def date_cutting_list(begin_year,begin_month,end_year=-1,end_month=-1):
    res={}
    if end_year==-1:
        end_year=begin_year
    if end_month==-1:
        end_month=begin_month
    
    if begin_year==end_year:  #不跨年的切片
        if begin_month>end_month:
            begin_month,end_month=end_month,begin_month
        
        month=[i for i in range(begin_month,end_month+1)]
        res[begin_year]=month
    elif begin_year<end_year:  #跨年的切片
        year=[i for i in range(begin_year,end_year)]
        month=[i for i in range(1,13)]
        for y in year:
            res[y]=month
        
        month=[i for i in range(begin_month,13)]
        res[begin_year]=month
        month=[i for i in range(1,end_month+1)]
        res[end_year]=month
        
    else:
        print('起始年度不应大于结束年度！')
    return res

def test(a,b,c=-1,d=-1):
    begin_year=a
    begin_month=b
    end_year=c
    end_month=d
    print(end_year,end_month)
    
    f=date_cutting_list(begin_year,begin_month,end_year,end_month)
    j=f.get(2021)
    print(j)
    
    
t=test(2018,3,2022,7)