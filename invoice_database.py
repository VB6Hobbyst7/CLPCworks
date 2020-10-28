# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 13:57:18 2020

@author: zhangxi
"""

import pymysql
import pandas as pd
from invoice_inspect import inspector
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#生成发票检查大表
rw_text=pd.read_csv('E:/OneDrive/国寿养老工作/invoice.txt',error_bad_lines=False)
y="2020"
m=["09",'08','10']

def grand_tab_gen():
    grand_tab=inspector(rw_text,y,m)
    #alert_tab = grand_tab[grand_tab["预警标志"] != ""]
    grand_tab[grand_tab['系统公文号']==""]
    
    for index,row in grand_tab.iterrows():
        if '错误' in row['预警标志']:
            grand_tab.loc[index,'系统公文号']='作废'
    '''
    engine = create_engine('mysql+pymysql://root:abcd1234@localhost:3306/clpc_ah?charset=utf8')
    
    pd.io.sql.to_sql(grand_tab,'invoice777',engine,if_exists='append')
    DbSession = sessionmaker()
    session = DbSession()
    session.commit()
    '''
    return grand_tab


def OAfile_gen():             #导出数据库中公文号为空的表
    db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
    cursor = db.cursor()
    
    sql="select 发票号码,价税合计,销售方名称,报销部门（参考） from invoice where 系统公文号 is null or 系统公文号=''"
    cursor.execute(sql)
    rows=cursor.fetchall()
    x_tab=pd.DataFrame(index=rows,columns=['系统公文号'])
    x_tab=x_tab.reset_index()
    x_tab.sort_values(by='level_0',inplace=True)        
    x_tab.rename(columns={'level_0':'发票号码','level_1':'价税合计','level_2':"销售方名称",'level_3':"报销部门（参考）"},inplace=True)
    x_tab.to_excel('C:/Users/ZhangXi/Desktop/update_tosql.xlsx',index=False)
    cursor.close()
    db.close()
    return x_tab


def OAfile_update():                        #更新系统公文号
    update_tab=pd.read_excel('C:/Users/ZhangXi/Desktop/update_tosql.xlsx',dtype={'发票号码':str}).to_dict(orient='list')
    dict1=dict(zip(update_tab['发票号码'],update_tab['系统公文号']))
    dict2=dict(zip(update_tab['发票号码'],update_tab['报销部门（参考）']))
    db = pymysql.connect("localhost","root","abcd1234",'clpc_ah')
    cursor = db.cursor()
    temp1=update_tab['发票号码']
    sql1=("UPDATE invoice set 系统公文号=%s where 发票号码=%s;")
    sql2=("UPDATE invoice set 报销部门（参考）=%s where 发票号码=%s;")
    for j in range(len(temp1)):
        cursor.execute(sql1,(dict1.get(temp1[j]),temp1[j]))
        cursor.execute(sql2,(dict2.get(temp1[j]),temp1[j]))
    db.commit()
    cursor.close()
    db.close()

a="0"

a=input('请选择本次处理的任务：\n1-查验发票、生成数据库表预备导入\n2-导出数据库中空公文号的条目\n3-更新系统公文号\n>>>')

if a=="0":
    pass
elif a=="1":
    temp_tab=grand_tab_gen()
    temp_tab.to_excel('C:/Users/ZhangXi/Desktop/invoice_to_sql.xlsx',index=False)
    alert_tab = temp_tab[temp_tab["预警标志"] != ""]
elif a=="2":
    OAfile_gen()
elif a=="3":
    OAfile_update()
