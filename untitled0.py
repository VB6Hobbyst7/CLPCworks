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


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()




conn=create_engine("mysql+pymysql://clpc_ah:abcd1234@LocalDB/invoice?charset=uft-8"
                   ,echo=True)

DbSession = sessionmaker(bind=conn)
session = DbSession()

session.query(invoice).all()
session.close()

