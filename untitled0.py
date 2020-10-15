# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:13:33 2020

@author: zhangxi
"""

import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

test=pd.read_excel('C:/Users/ZhangXi/Desktop/to_sql.xlsx')

#for index,row in test.iterrows():
#    test.loc[index,'发票明细']=test.loc[index,'发票明细'].replace("\'","")


engine = create_engine('mysql+pymysql://root:abcd1234@localhost:3306/clpc_ah?charset=utf8')
    
pd.io.sql.to_sql(test,'invoice777',engine,if_exists='append')
DbSession = sessionmaker()
session = DbSession()
session.commit()
