# -*- coding: utf-8 -*-
"""
Created on Fri Nov  6 08:56:39 2020

@author: zhangxi
"""
import pandas as pd
import pymysql
import numpy as np
import os
import datetime
import time
import functools
import sys

from gadgets import timer
'''

sql=("SELECT * from potted_funds_records UNION select * from open_funds_records;")
cursor.execute(sql)
temp=cursor.fetchall()

columnDes = cursor.description #获取连接对象的描述信息
columnNames = [columnDes[i][0] for i in range(len(columnDes))] #获取列名
data_rw= pd.DataFrame([list(i) for i in temp],columns=columnNames)
'''
test_tab=pd.read_excel('C:/Users/ZhangXi/Desktop/invoice_to_sql.xlsx',dtype={'发票号码':str})

db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
cursor = db.cursor()
col=str(tuple(test_tab.columns.values))
col=col.replace("\'"," ")

for i in range(len(test_tab)):
    rec=str(tuple(test_tab.loc[i,:]))
    rec=rec.replace('nan','"(null)"')
    insert_sql="insert into invoice%s values%s;" %(col,rec)
    cursor.execute(insert_sql)
    
try:
    db.commit()
except:
    db.rollback()
    
cursor.close
db.close
    
