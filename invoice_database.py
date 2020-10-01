# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 13:57:18 2020

@author: zhangxi
"""

import pymysql
import pandas as pd
from invoice_inspect import inspector
from sqlalchemy import create_engine

'''
rw_text=pd.read_csv('E:/OneDrive/Python工作/CLPCworks/invoice.txt',error_bad_lines=False)
y="2020"
m=["07",'08','09']
grand_tab=inspector(rw_text,y,m)
alert_tab = grand_tab[grand_tab["预警标志"] != ""]
OA_filling=grand_tab[grand_tab['系统公文号']==""]

##########################################################

db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
cursor = db.cursor()
sql="select 发票号码,价税合计,销售方名称 from invoice where 系统公文号 is null "
cursor.execute(sql)
rows=cursor.fetchall()

x_tab=pd.DataFrame(index=rows,columns=['系统公文号'])
x_tab=x_tab.reset_index()
x_tab.sort_values(by='level_0',inplace=True)        
x_tab.rename(columns={'level_0':'发票号码','level_1':'价税合计','level_2':"销售方名称"},inplace=True)
x_tab.to_excel('C:/Users/ZhangXi/Desktop/at.xlsx')

##################################################导出关联表
'''


#db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
#cursor = db.cursor()
#sql="select 发票号码,价税合计,销售方名称 from invoice where 系统公文号 is null "
#cursor.execute(sql)
#rows=cursor.fetchall()

update_tab=pd.read_excel('C:/Users/ZhangXi/Desktop/at.xlsx')
engine = create_engine('mysql+pymysql://root:abcd1234@localhost:3306/clpc_ah?charset=utf8',echo=True)
conn=engine.connect()
sql="select 发票号码,价税合计,销售方名称 from invoice "
f=conn.execute(sql)

#pd.io.sql.to_sql(grand_tab,conn,'invoice','clpc_ah',if_exists='append')
