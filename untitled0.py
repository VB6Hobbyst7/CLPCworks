# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 22:19:41 2020

@author: zhangxi
"""

import pymysql
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from invoice_inspect import inspector

#engine = create_engine('mysql+pymysql://root:abcd1234@localhost:3306/clpc_ah?charset=utf8')
df=pd.DataFrame(index=range(10),columns=list('cons'))
for i in range(len(df)):
    for j in range(len(df.columns)):
        df.iloc[i,j]=(i+j)*i*3
        
e=[]
for i in range(len(df)):
    d=tuple(df.iloc[i,:])
    e.append(d)

db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
cursor = db.cursor()

sql=("insert into test(c,o,n,s)value(%float,%s,%s,%s);")
cursor.executemany(sql,e)   

db.commit()
cursor.close()
db.close()


print(e)

'''
engine = create_engine('mysql+pymysql://root:abcd1234@localhost:3306/clpc_ah?charset=utf8')
    
pd.io.sql.to_sql(df,'test_tab',engine,if_exists='append',index=False,index_label=False)
DbSession = sessionmaker()
session = DbSession()
session.commit()
'''
'''
rw_text=pd.read_csv('E:/OneDrive/Python工作/CLPCworks/invoice.txt',error_bad_lines=False)
y="2020"
m=["07",'08','09']

def grand_tab_gen():
    grand_tab=inspector(rw_text,y,m)
    #alert_tab = grand_tab[grand_tab["预警标志"] != ""]
    grand_tab[grand_tab['系统公文号']==""]
    
    for index,row in grand_tab.iterrows():
        if '错误' in row['预警标志']:
            grand_tab.loc[index,'系统公文号']='作废'
    engine = create_engine('mysql+pymysql://root:abcd1234@localhost:3306/clpc_ah?charset=utf8')
    
    pd.io.sql.to_sql(grand_tab,'invoice_test',engine,schema='clpc_ah',if_exists='append',index=False,index_label=False)
    DbSession = sessionmaker()
    session = DbSession()
    session.commit()
    
    return grand_tab
yy=grand_tab_gen()
yy.to_excel('C:/Users/ZhangXi/Desktop/to_s1ql.xlsx')
'''