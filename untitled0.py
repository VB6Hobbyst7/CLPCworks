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

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(
  "mysql+pymysql://root:abcd1234@localhost/clpc_ah?charset=utf8mb4", 
  echo=True, 
  max_overflow=5)

l=engine.execute("select * from invoice;")
#r=pd.DataFrame(l.fetchall())
md=sqlalchemy.MetaData()
table = sqlalchemy.Table('invoice', md, autoload=True, autoload_with=engine)
col=table.c

rec=pd.DataFrame(l.fetchall(),columns=col)

Base=declarative_base()

class User(Base):
    __tablename__='发票入库记录'
    id=column(Integer,Sequence())