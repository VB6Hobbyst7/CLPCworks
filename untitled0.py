# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 20:55:01 2020

@author: zhangxi
"""

'''
import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np

from sklearn.datasets import load_iris
iris = load_iris()
features = iris.data.T
plt.scatter(features[0], features[1], alpha=0.2,
s=100*features[3], c=iris.target, cmap='viridis')
plt.xlabel(iris.feature_names[0])
plt.ylabel(iris.feature_names[1]);
'''
import functools
import time

import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine ,Column,String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+pymysql://root:abcd1234@localhost:3306/clpc_ah?charset=utf8',echo=True)
DBSession = sessionmaker(bind=engine)
Base=declarative_base()
session=DBSession()

invoice_list=engine.execute('select * from invoice').fetchall()